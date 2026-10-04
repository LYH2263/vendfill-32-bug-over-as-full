from app.services.page_split import present_full, present_summary, present_ticket


def _payload():
    return {
        "id": 9,
        "lines": [
            {"lane_id": 1, "slot_no": "A1", "gap": 7, "fill_qty": 4, "status": "need_fill"},
            {"lane_id": 2, "slot_no": "A2", "gap": 0, "fill_qty": 0, "status": "full"},
            {"lane_id": 3, "slot_no": "C2", "gap": -2, "fill_qty": 0, "status": "overbooked"},
        ],
        "need_fill_count": 1,
        "full_count": 1,
        "overbooked_count": 1,
    }


def test_summary_counts_full_and_overbooked_separately():
    s = present_summary(1, _payload())
    # 超占与满仓是两个互斥计数，不能捏成一个“补量为零”的数
    assert s["full_count"] == 1
    assert s["overbooked_count"] == 1
    assert s["need_fill_count"] == 1
    # 汇总总量照小票补量合计；超占行补量 0，不拿负 gap 冲减
    assert s["total_fill"] == 4


def test_full_list_contains_only_full_lanes():
    body = present_full(1, _payload())
    ids = {l["lane_id"] for l in body["lanes"]}
    assert ids == {2}  # 满仓名单不得混入超占，也不收待补行


def test_ticket_keeps_snapshot_rows_and_words():
    payload = _payload()
    t = present_ticket(payload)
    # 小票照快照逐行呈现：超占行仍是超占、补量 0，历史单不被回刷
    by_id = {l["lane_id"]: l for l in t["lines"]}
    assert by_id[3]["status"] == "overbooked" and by_id[3]["fill_qty"] == 0
    assert by_id[2]["status"] == "full"
    assert t["total_fill"] == 4


def test_snapshot_words_survive_later_change():
    # 旧票快照写的是满仓，即便现在该货道已超占，打开旧票仍显示满仓
    old = {"lines": [{"lane_id": 5, "gap": 0, "fill_qty": 0, "status": "full"}]}
    t = present_ticket(old)
    assert t["lines"][0]["status"] == "full"
    body = present_full(1, old)
    assert [l["lane_id"] for l in body["lanes"]] == [5]
