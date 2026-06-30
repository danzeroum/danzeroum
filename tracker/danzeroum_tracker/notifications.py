"""Notificações de alertas (oportunidades de alta aderência).

Interface agnóstica: ``NullNotifier`` (default, no-op seguro) e ``EmailNotifier``
(SMTP via smtplib, reusa as variáveis SMTP_* do site). O transporte SMTP é
injetável, então dá para testar sem rede.
"""

from __future__ import annotations

import html
import smtplib
from abc import ABC, abstractmethod
from collections.abc import Callable
from email.message import EmailMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from danzeroum_tracker.config import Settings

Transport = Callable[..., None]


def format_alerts(result: dict) -> tuple[str, str, str]:
    """Monta (assunto, corpo_texto, corpo_html) a partir do resultado da coleta."""
    alerts = result.get("alerts", [])
    n = len(alerts)
    subject = f"[Danzeroum] {n} nova(s) oportunidade(s) de licitação"

    text_lines = [f"{n} oportunidade(s) com boa aderência:", ""]
    html_rows = []
    for a in alerts:
        title = a.get("title") or ""
        fit = a.get("fit_score")
        fit_s = f"{fit:.2f}" if isinstance(fit, int | float) else "—"
        rec = a.get("recommendation") or "—"
        url = a.get("url") or ""
        deadline = a.get("deadline") or "—"
        text_lines.append(f"- [{rec} fit={fit_s}] {title}")
        text_lines.append(f"  prazo={deadline} | {url}")
        # Escapa os valores interpolados (títulos/URLs de editais podem ter & < >).
        e_title, e_url = html.escape(title), html.escape(url)
        e_rec, e_deadline = html.escape(rec), html.escape(str(deadline))
        html_rows.append(
            f"<li><b>[{e_rec} fit={fit_s}]</b> {e_title}<br>"
            f"<small>prazo={e_deadline} · <a href='{e_url}'>{e_url}</a></small></li>"
        )
    text = "\n".join(text_lines)
    html_body = f"<p>{n} oportunidade(s) com boa aderência:</p><ul>{''.join(html_rows)}</ul>"
    return subject, text, html_body


class Notifier(ABC):
    name = "abstract"

    @abstractmethod
    def notify(self, result: dict) -> int:
        """Envia alertas do resultado da coleta. Retorna quantos foram enviados."""


class NullNotifier(Notifier):
    """No-op seguro: não envia nada (default quando SMTP não está configurado)."""

    name = "null"

    def notify(self, result: dict) -> int:
        return 0


def _smtplib_transport(
    *,
    host: str,
    port: int,
    encryption: str,
    user: str,
    password: str,
    message: EmailMessage,
) -> None:  # pragma: no cover - exercitado só com SMTP real
    enc = (encryption or "").lower()
    if enc == "ssl":
        with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            if enc in ("tls", "starttls"):
                smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(message)


class EmailNotifier(Notifier):
    name = "email"

    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        from_addr: str,
        from_name: str,
        to_addr: str,
        encryption: str = "ssl",
        transport: Transport | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_addr = from_addr
        self.from_name = from_name
        self.to_addr = to_addr
        self.encryption = encryption
        self._transport = transport or _smtplib_transport

    def notify(self, result: dict) -> int:
        alerts = result.get("alerts", [])
        if not alerts:
            return 0
        subject, text, html = format_alerts(result)
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_addr}>" if self.from_name else self.from_addr
        msg["To"] = self.to_addr
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")
        self._transport(
            host=self.host,
            port=self.port,
            encryption=self.encryption,
            user=self.user,
            password=self.password,
            message=msg,
        )
        return len(alerts)


def build_notifier(settings: Settings, transport: Transport | None = None) -> Notifier:
    """E-mail se SMTP_HOST + MAIL_TO estiverem configurados; senão, no-op."""
    if settings.smtp_host and settings.mail_to:
        return EmailNotifier(
            host=settings.smtp_host,
            port=settings.smtp_port,
            user=settings.smtp_user,
            password=settings.smtp_pass,
            from_addr=settings.smtp_from or settings.smtp_user,
            from_name=settings.smtp_from_name,
            to_addr=settings.mail_to,
            encryption=settings.smtp_encryption,
            transport=transport,
        )
    return NullNotifier()


# ── Telegram (multicanal) ────────────────────────────────────────────────────────

TelegramPoster = Callable[..., None]


def _requests_telegram_post(*, bot_token: str, chat_id: str, text: str) -> None:  # pragma: no cover
    import requests

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=30,
    )


class TelegramNotifier(Notifier):
    name = "telegram"

    def __init__(
        self, *, bot_token: str, chat_id: str, poster: TelegramPoster | None = None
    ) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._poster = poster or _requests_telegram_post

    def notify(self, result: dict) -> int:
        alerts = result.get("alerts", [])
        if not alerts:
            return 0
        _subject, text, _html = format_alerts(result)
        self._poster(bot_token=self.bot_token, chat_id=self.chat_id, text=text)
        return len(alerts)


class MultiNotifier(Notifier):
    """Envia por todos os canais configurados (best-effort por canal)."""

    name = "multi"

    def __init__(self, notifiers: list[Notifier]) -> None:
        self.notifiers = notifiers

    def notify(self, result: dict) -> int:
        total = 0
        for n in self.notifiers:
            try:
                total += n.notify(result)
            except Exception:  # noqa: BLE001 - um canal não derruba os demais
                continue
        return total


def build_all_notifiers(
    settings: Settings,
    *,
    transport: Transport | None = None,
    telegram_poster: TelegramPoster | None = None,
) -> Notifier:
    """Compõe e-mail + Telegram conforme configurados. Sem nenhum, no-op."""
    channels: list[Notifier] = []
    email = build_notifier(settings, transport=transport)
    if not isinstance(email, NullNotifier):
        channels.append(email)
    if settings.telegram_bot_token and settings.telegram_chat_id:
        channels.append(
            TelegramNotifier(
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
                poster=telegram_poster,
            )
        )
    if not channels:
        return NullNotifier()
    if len(channels) == 1:
        return channels[0]
    return MultiNotifier(channels)
