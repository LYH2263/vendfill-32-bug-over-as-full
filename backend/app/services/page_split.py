"""小票 / 满仓名单 / 汇总的展示口径。

唯一事实源是单据快照里每行的 fill_engine 状态（need_fill/full/overbooked），
各页只能照快照归类，不得自行按 gap/fill_qty 另算：
  - 小票行：快照写的是什么就是什么（历史单保持生成当时的字）；
  - 满仓名单：只收 status == full；超占与满仓互斥，绝不混入；
  - 汇总：超占、满仓两个计数分开统计，不得捏成一个数。
"""
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
    lines = _lines(payload)
    # 满仓名单只列满仓：超占（gap < 0）与满仓互斥，绝不靠“补量为 0”混入。
    lanes = [l for l in lines if str(l.get("status") or "") == "full"]
    return {"location_id": location_id, "lanes": lanes}


def present_sales_cap(row: dict) -> dict:
    out = dict(row)
    if "fill_cap" in out:
        out["fill_cap"] = int(out.get("gap") or out.get("fill_cap") or 0)
    return out
