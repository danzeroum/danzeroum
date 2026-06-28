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
from danzeroum_tracker.adapters.pncp import PNCPAdapter
from danzeroum_tracker.config import Settings
from danzeroum_tracker.pipeline import run_collection
from danzeroum_tracker.scoring import SCORE_SCHEMA, Scorer, get_scorer
from danzeroum_tracker.storage import build_repository
from danzeroum_tracker.storage.base import TenderRepository


def build_adapters(settings: Settings, session=None) -> list[OrgaoAdapter]:
    """V1: apenas PNCP. Novos órgãos entram aqui sem mexer no core."""
    return [
        PNCPAdapter(
            base_url=settings.pncp_base_url,
            uf=settings.uf,
            keywords=settings.keywords,
            page_size=settings.page_size,
            max_pages=settings.max_pages,
            timeout=settings.request_timeout,
            session=session,
        )
    ]


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
    scorer = scorer or get_scorer(settings.scorer)
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
    out: TextIO = sys.stdout,
) -> int:
    repo = repo if repo is not None else build_repository(settings.database_url)
    adapters = adapters if adapters is not None else build_adapters(settings)
    scorer = scorer or get_scorer(settings.scorer)
    result = run_collection(adapters, repo, scorer, min_fit_alert=settings.min_fit_alert)
    _emit(result.to_dict(), out)
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
    iterations: int | None = None,
    sleep_fn=time.sleep,
    out: TextIO = sys.stdout,
) -> int:
    """Loop de baixa frequência (poucos acessos/dia). ``iterations`` limita p/ teste."""
    repo = repo if repo is not None else build_repository(settings.database_url)
    interval_s = max(settings.collect_interval_hours, 0.0) * 3600.0
    count = 0
    while True:
        cmd_collect(settings, repo=repo, adapters=adapters, scorer=scorer, out=out)
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
    if args.command == "schedule":
        return cmd_schedule(settings, out=out)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
