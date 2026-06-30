from danzeroum_tracker.config import Settings
from danzeroum_tracker.notifications import (
    EmailNotifier,
    MultiNotifier,
    NullNotifier,
    TelegramNotifier,
    build_all_notifiers,
    build_notifier,
    format_alerts,
)

RESULT = {
    "collected": 2,
    "new": 1,
    "scored": 1,
    "alerts": [
        {
            "title": "Suporte de TI",
            "url": "http://x/1",
            "deadline": "2026-12-30T18:00:00",
            "fit_score": 0.8,
            "risk_score": 0.3,
            "recommendation": "GO",
        }
    ],
}


def test_format_alerts():
    subject, text, html = format_alerts(RESULT)
    assert "1 nova" in subject
    assert "Suporte de TI" in text
    assert "<ul>" in html and "Suporte de TI" in html


def test_format_alerts_escapes_html():
    result = {
        "alerts": [
            {
                "title": "Suporte <TI> & Redes",
                "url": "http://x/?a=1&b=2",
                "deadline": "2026-12-30",
                "fit_score": 0.8,
                "recommendation": "GO",
            }
        ]
    }
    _subject, text, html_body = format_alerts(result)
    # HTML escapado: sem '<TI>' cru nem '&' solto.
    assert "<TI>" not in html_body
    assert "&lt;TI&gt;" in html_body
    assert "&amp;" in html_body
    # O corpo texto preserva o original (não é HTML).
    assert "Suporte <TI> & Redes" in text


def test_null_notifier_noop():
    assert NullNotifier().notify(RESULT) == 0


def test_email_notifier_sends_via_transport():
    captured = {}

    def fake_transport(*, host, port, encryption, user, password, message):
        captured.update(
            host=host, port=port, encryption=encryption,
            subject=message["Subject"], to=message["To"], from_=message["From"],
            is_multipart=message.is_multipart(),
        )

    notifier = EmailNotifier(
        host="smtp.test", port=465, user="u", password="p",
        from_addr="from@d.com", from_name="Rastreador", to_addr="to@d.com",
        encryption="ssl", transport=fake_transport,
    )
    sent = notifier.notify(RESULT)
    assert sent == 1
    assert captured["host"] == "smtp.test"
    assert captured["to"] == "to@d.com"
    assert captured["from_"] == "Rastreador <from@d.com>"
    assert captured["is_multipart"] is True  # texto + html


def test_email_notifier_skips_when_no_alerts():
    calls = []
    notifier = EmailNotifier(
        host="smtp.test", port=465, user="u", password="p",
        from_addr="from@d.com", from_name="", to_addr="to@d.com",
        transport=lambda **k: calls.append(k),
    )
    assert notifier.notify({"alerts": []}) == 0
    assert calls == []


def test_build_notifier_null_when_unconfigured():
    assert isinstance(build_notifier(Settings.from_env({})), NullNotifier)


def test_build_notifier_email_when_configured():
    settings = Settings.from_env(
        {"SMTP_HOST": "smtp.test", "MAIL_TO": "to@d.com", "SMTP_USER": "u"}
    )
    notifier = build_notifier(settings, transport=lambda **k: None)
    assert isinstance(notifier, EmailNotifier)


# ── Telegram / multicanal ────────────────────────────────────────────────────────


def test_telegram_notifier_posts_text():
    captured = {}

    def fake_poster(*, bot_token, chat_id, text):
        captured.update(bot_token=bot_token, chat_id=chat_id, text=text)

    n = TelegramNotifier(bot_token="tok", chat_id="42", poster=fake_poster)
    sent = n.notify(RESULT)
    assert sent == 1
    assert captured["bot_token"] == "tok"
    assert captured["chat_id"] == "42"
    assert "Suporte de TI" in captured["text"]


def test_telegram_notifier_skips_when_no_alerts():
    calls = []
    n = TelegramNotifier(bot_token="t", chat_id="1", poster=lambda **k: calls.append(k))
    assert n.notify({"alerts": []}) == 0
    assert calls == []


def test_multi_notifier_sums_and_isolates_failures():
    class Boom:
        def notify(self, result):
            raise RuntimeError("canal quebrado")

    class Ok:
        def notify(self, result):
            return 2

    assert MultiNotifier([Ok(), Boom(), Ok()]).notify(RESULT) == 4


def test_build_all_notifiers_composes_email_and_telegram():
    settings = Settings.from_env({
        "SMTP_HOST": "smtp.test", "MAIL_TO": "to@d.com", "SMTP_USER": "u",
        "TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_CHAT_ID": "42",
    })
    n = build_all_notifiers(settings, transport=lambda **k: None, telegram_poster=lambda **k: None)
    assert isinstance(n, MultiNotifier)
    assert {x.name for x in n.notifiers} == {"email", "telegram"}


def test_build_all_notifiers_telegram_only():
    settings = Settings.from_env({"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_CHAT_ID": "42"})
    assert isinstance(build_all_notifiers(settings), TelegramNotifier)


def test_build_all_notifiers_null_when_unconfigured():
    assert isinstance(build_all_notifiers(Settings.from_env({})), NullNotifier)
