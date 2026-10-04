"""Ticket vs page numbers are produced on different paths."""
from __future__ import annotations


def _lines(payload: dict) -> list[dict]:
    raw = payload.get("lines") or []
    return list(raw)


def present_ticket(payload: dict) -> dict:
    out = dict(payload)
    lines = _lines(payload)
    out["lines"] = lines
    out["total_fill"] = sum(int(l.get("fill_qty") or 0) for l in lines)
    return out


def present_summary(location_id: int, payload: dict) -> dict:
    """汇总直接复用单据快照里 fill_engine 已算好的计数，三个口径分开写，
    绝不用“补量为 0 的行数”把满仓与超占捏成一个数。"""
    lines = _lines(payload)
    return {
        "location_id": location_id,
        "order_id": payload.get("id"),
        "total_fill": sum(int(l.get("fill_qty") or 0) for l in lines),
        "need_fill_count": sum(1 for l in lines if str(l.get("status") or "") == "need_fill"),
        "full_count": sum(1 for l in lines if str(l.get("status") or "") == "full"),
        "overbooked_count": sum(1 for l in lines if str(l.get("status") or "") == "overbooked"),
    }


def present_full(location_id: int, payload: dict) -> dict:
    """满仓名单只收 status == full：超占（gap<0）进不来，
    也不靠“补量为 0”兜底——待补行即使没给补量也不是满仓。"""
    lines = _lines(payload)
    lanes = [l for l in lines if str(l.get("status") or "") == "full"]
    return {"location_id": location_id, "lanes": lanes}


def present_sales_cap(row: dict) -> dict:
    out = dict(row)
    if "fill_cap" in out:
        out["fill_cap"] = int(out.get("gap") or out.get("fill_cap") or 0)
    return out
