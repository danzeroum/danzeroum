"""CLI do rastreador.

Comandos:
  schema             imprime o JSON Schema do scorer
  search             busca + pontua editais (não persiste) → JSON
  collect            coleta + dedupe + score + persiste → resumo JSON
  list               lista editais persistidos
  schedule           loop: roda 'collect' a cada COLLECT_INTERVAL_HOURS

Uso típico (Docker): ``python -m danzeroum_tracker schedule``
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Iterable
from typing import TextIO

from danzeroum_tracker import __version__
from danzeroum_tracker.adapters.base import OrgaoAdapter
from danzeroum_tracker.adapters.comprasgov import ComprasGovAdapter
from danzeroum_tracker.adapters.pncp import PNCPAdapter
from danzeroum_tracker.adapters.scraper import ComprasSPAdapter, PrefeituraSPAdapter
from danzeroum_tracker.config import Settings
from danzeroum_tracker.notifications import Notifier, build_all_notifiers
from danzeroum_tracker.pipeline import run_collection
from danzeroum_tracker.reporting import build_report, render_markdown, render_text
from danzeroum_tracker.scoring import SCORE_SCHEMA, Scorer, get_scorer
from danzeroum_tracker.storage import build_repository
from danzeroum_tracker.storage.base import TenderRepository


def build_adapters(settings: Settings, session=None) -> list[OrgaoAdapter]:
    """Constrói os adaptadores ativos (settings.sources). Novos órgãos entram aqui."""
    common = dict(
        uf=settings.uf,
        keywords=settings.keywords,
        page_size=settings.page_size,
        max_pages=settings.max_pages,
        timeout=settings.request_timeout,
        session=session,
    )
    factories = {
        "pncp": lambda: PNCPAdapter(
            base_url=settings.pncp_base_url,
            modalidades=settings.modalidades,
            horizon_days=settings.proposal_horizon_days,
            **common,
        ),
        "comprasgov": lambda: ComprasGovAdapter(base_url=settings.comprasgov_base_url, **common),
        "comprassp": lambda: ComprasSPAdapter(base_url=settings.comprassp_base_url, **common),
        "prefsp": lambda: PrefeituraSPAdapter(base_url=settings.prefsp_base_url, **common),
    }
    adapters: list[OrgaoAdapter] = []
    for name in settings.sources:
        factory = factories.get(name)
        if factory is None:
            raise ValueError(
                f"fonte desconhecida: {name!r} (disponíveis: {', '.join(factories)})"
            )
        adapters.append(factory())
    return adapters


def _emit(data, out: TextIO) -> None:
    json.dump(data, out, ensure_ascii=False, indent=2, default=str)
    out.write("\n")


def cmd_schema(out: TextIO) -> int:
    _emit(SCORE_SCHEMA, out)
    return 0


def cmd_search(
    settings: Settings,
    *,
    limit: int = 20,
    adapters: Iterable[OrgaoAdapter] | None = None,
    scorer: Scorer | None = None,
    out: TextIO = sys.stdout,
) -> int:
    adapters = adapters if adapters is not None else build_adapters(settings)
    scorer = scorer or get_scorer(settings.scorer, settings=settings)
    results = []
    for adapter in adapters:
        for tender in adapter.collect():
            score = scorer.score(tender)
            results.append({**tender.to_dict(), "score": score.to_dict()})
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    results.sort(key=lambda r: r["score"]["fit_score"], reverse=True)
    _emit(results, out)
    return 0


def cmd_collect(
    settings: Settings,
    *,
    repo: TenderRepository | None = None,
    adapters: Iterable[OrgaoAdapter] | None = None,
    scorer: Scorer | None = None,
    notifier: Notifier | None = None,
    out: TextIO = sys.stdout,
) -> int:
    repo = repo if repo is not None else build_repository(settings.database_url)
    adapters = adapters if adapters is not None else build_adapters(settings)
    scorer = scorer or get_scorer(settings.scorer, settings=settings)
    notifier = notifier if notifier is not None else build_all_notifiers(settings)
    result = run_collection(adapters, repo, scorer, min_fit_alert=settings.min_fit_alert)
    payload = result.to_dict()
    # A coleta já está persistida; uma falha no envio de e-mail NÃO pode derrubar
    # o comando nem esconder o resultado. Captura e segue.
    try:
        payload["notified"] = notifier.notify(payload)
    except Exception as exc:  # noqa: BLE001 - notificação é best-effort
        payload["notified"] = 0
        payload["notify_error"] = str(exc)
    _emit(payload, out)
    return 0


def cmd_certs_alert(
    settings: Settings,
    *,
    within_days: int = 30,
    transport=None,
    rows: list[dict] | None = None,
    out: TextIO = sys.stdout,
) -> int:
    """Varre vencimentos de certidões/documentos e (best-effort) envia e-mail."""
    from danzeroum_tracker.certs import run_cert_alert

    payload = run_cert_alert(settings, within_days=within_days, rows=rows, transport=transport)
    _emit(payload, out)
    return 0


def cmd_report(
    settings: Settings,
    *,
    limit: int = 10,
    fmt: str = "text",
    repo: TenderRepository | None = None,
    out: TextIO = sys.stdout,
) -> int:
    repo = repo if repo is not None else build_repository(settings.database_url)
    rows = repo.list_scored(limit=5000)  # estatísticas sobre o acervo; top-N no display
    report = build_report(rows, top_n=limit)
    if fmt == "json":
        _emit(report, out)
    elif fmt in ("md", "markdown"):
        out.write(render_markdown(report) + "\n")
    else:
        out.write(render_text(report) + "\n")
    return 0


def cmd_list(
    settings: Settings,
    *,
    limit: int = 50,
    repo: TenderRepository | None = None,
    out: TextIO = sys.stdout,
) -> int:
    repo = repo if repo is not None else build_repository(settings.database_url)
    _emit(repo.list_tenders(limit=limit), out)
    return 0


def cmd_schedule(
    settings: Settings,
    *,
    repo: TenderRepository | None = None,
    adapters: Iterable[OrgaoAdapter] | None = None,
    scorer: Scorer | None = None,
    notifier: Notifier | None = None,
    iterations: int | None = None,
    sleep_fn=time.sleep,
    out: TextIO = sys.stdout,
) -> int:
    """Loop de baixa frequência (poucos acessos/dia). ``iterations`` limita p/ teste."""
    repo = repo if repo is not None else build_repository(settings.database_url)
    interval_s = max(settings.collect_interval_hours, 0.0) * 3600.0
    count = 0
    while True:
        cmd_collect(
            settings, repo=repo, adapters=adapters, scorer=scorer, notifier=notifier, out=out
        )
        # Aviso de vencimento de certidões — diário, junto da coleta (best-effort).
        try:
            from danzeroum_tracker.certs import run_cert_alert

            _emit({"certs_alert": run_cert_alert(settings)}, out)
        except Exception as exc:  # noqa: BLE001 - aviso é best-effort, não derruba o loop
            _emit({"certs_alert_error": str(exc)}, out)
        count += 1
        if iterations is not None and count >= iterations:
            return 0
        sleep_fn(interval_s)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="danzeroum-tracker", description="Rastreador de licitações")
    p.add_argument("--version", action="version", version=f"danzeroum-tracker {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("schema", help="imprime o JSON Schema do scorer")

    sp = sub.add_parser("search", help="busca + pontua (não persiste)")
    sp.add_argument("--limit", type=int, default=20)

    sub.add_parser("collect", help="coleta + dedupe + score + persiste")

    lp = sub.add_parser("list", help="lista editais persistidos")
    lp.add_argument("--limit", type=int, default=50)

    rp = sub.add_parser("report", help="relatório de oportunidades (do acervo)")
    rp.add_argument("--limit", type=int, default=10)
    rp.add_argument("--format", dest="fmt", choices=["text", "md", "json"], default="text")

    cp = sub.add_parser("certs-alert", help="avisa certidões/documentos a vencer (e-mail)")
    cp.add_argument("--within", dest="within_days", type=int, default=30)

    sub.add_parser("schedule", help="loop periódico (Docker)")
    return p


def main(argv: list[str] | None = None, out: TextIO = sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()

    if args.command == "schema":
        return cmd_schema(out)
    if args.command == "search":
        return cmd_search(settings, limit=args.limit, out=out)
    if args.command == "collect":
        return cmd_collect(settings, out=out)
    if args.command == "list":
        return cmd_list(settings, limit=args.limit, out=out)
    if args.command == "report":
        return cmd_report(settings, limit=args.limit, fmt=args.fmt, out=out)
    if args.command == "certs-alert":
        return cmd_certs_alert(settings, within_days=args.within_days, out=out)
    if args.command == "schedule":
        return cmd_schedule(settings, out=out)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
