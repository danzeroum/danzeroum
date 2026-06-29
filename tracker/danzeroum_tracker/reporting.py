"""Geração de relatório de oportunidades a partir do repositório."""

from __future__ import annotations

from collections import Counter
from typing import Any


def build_report(rows: list[dict], top_n: int = 10) -> dict[str, Any]:
    """Resumo: total, breakdown por recomendação e top-N por aderência."""
    by_rec: Counter[str] = Counter()
    for r in rows:
        by_rec[r.get("recommendation") or "SEM_SCORE"] += 1
    top = sorted(rows, key=lambda r: (r.get("fit_score") or 0.0), reverse=True)[:top_n]
    return {
        "total": len(rows),
        "por_recomendacao": dict(by_rec),
        "top": [
            {
                "source": r.get("source"),
                "external_id": r.get("external_id"),
                "title": r.get("title"),
                "url": r.get("url"),
                "budget_estimate": _num(r.get("budget_estimate")),
                "deadline": _iso(r.get("deadline")),
                "fit_score": _num(r.get("fit_score")),
                "risk_score": _num(r.get("risk_score")),
                "recommendation": r.get("recommendation"),
            }
            for r in top
        ],
    }


def _num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    iso = getattr(value, "isoformat", None)
    return iso() if callable(iso) else str(value)


def _money(value: Any) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    # PNCP/Comprasnet devolve 0 quando o valor estimado é sigiloso/não divulgado.
    # Exibir "R$ 0,00" enganaria; mostramos "—" (não informado).
    if v <= 0:
        return "—"
    return f"R$ {v:,.2f}"


def _fit(value: Any) -> str:
    """Formata aderência (0-1). Aceita float, int e Decimal (Postgres NUMERIC)."""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "—"


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "Relatório de Oportunidades — Danzeroum",
        f"Total de editais: {report['total']}",
        "Por recomendação: "
        + ", ".join(f"{k}={v}" for k, v in sorted(report["por_recomendacao"].items())),
        "",
        "Top oportunidades (por aderência):",
    ]
    if not report["top"]:
        lines.append("  (nenhuma oportunidade pontuada ainda — rode 'collect')")
    for i, r in enumerate(report["top"], 1):
        fit_s = _fit(r.get("fit_score"))
        lines.append(
            f"  {i}. [{r.get('recommendation') or '—'} fit={fit_s}] "
            f"{(r.get('title') or '')[:80]} | {_money(r.get('budget_estimate'))} | "
            f"prazo={r.get('deadline') or '—'} | {r.get('url') or ''}"
        )
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    out = [
        "# Relatório de Oportunidades — Danzeroum",
        "",
        f"- **Total de editais:** {report['total']}",
        "- **Por recomendação:** "
        + ", ".join(f"`{k}`={v}" for k, v in sorted(report["por_recomendacao"].items())),
        "",
        "## Top oportunidades (por aderência)",
        "",
    ]
    if not report["top"]:
        out.append("_Nenhuma oportunidade pontuada ainda — rode `collect`._")
        return "\n".join(out)
    out += [
        "| # | Rec. | Fit | Objeto | Valor | Prazo | Link |",
        "|---|------|-----|--------|-------|-------|------|",
    ]
    for i, r in enumerate(report["top"], 1):
        fit_s = _fit(r.get("fit_score"))
        title = (r.get("title") or "").replace("|", "/")[:80]
        out.append(
            f"| {i} | {r.get('recommendation') or '—'} | {fit_s} | {title} | "
            f"{_money(r.get('budget_estimate'))} | {r.get('deadline') or '—'} | "
            f"{r.get('url') or ''} |"
        )
    return "\n".join(out)
