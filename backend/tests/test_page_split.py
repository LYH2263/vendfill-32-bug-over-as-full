from app.services.page_split import present_full, present_summary, present_ticket


def test_summary_counts_three_statuses_separately():
    # 三个口径分开数：不得把满仓和超占捏成一个 full_count
    payload = {
        "id": 9,
        "lines": [
            {"lane_id": 1, "gap": 7, "fill_qty": 4, "status": "need_fill"},
            {"lane_id": 2, "gap": 0, "fill_qty": 0, "status": "full"},
            {"lane_id": 3, "gap": -1, "fill_qty": 0, "status": "overbooked"},
        ],
        "need_fill_count": 1,
        "full_count": 1,
        "overbooked_count": 1,
    }
    s = present_summary(1, payload)
    assert s["total_fill"] == 4             # 建议补货总量取补量，不用 gap 凑
    assert s["need_fill_count"] == 1
    assert s["full_count"] == 1
    assert s["overbooked_count"] == 1


def test_full_list_keeps_only_full_status():
    # 满仓名单只收 status == full：超占和补量为 0 的非满仓行都不得混入
    payload = {
        "lines": [
            {"lane_id": 1, "fill_qty": 0, "status": "full", "reason": "满仓"},
            {"lane_id": 2, "fill_qty": 3, "status": "need_fill", "reason": ""},
            {"lane_id": 3, "fill_qty": 0, "status": "overbooked", "reason": "超占"},
            {"lane_id": 4, "fill_qty": 0, "status": "need_fill", "reason": ""},
        ]
    }
    body = present_full(1, payload)
    ids = {l["lane_id"] for l in body["lanes"]}
    assert ids == {1}


def test_ticket_keeps_row_fill_qty():
    payload = {"lines": [{"lane_id": 1, "fill_qty": 4, "gap": 9}]}
    t = present_ticket(payload)
    assert t["total_fill"] == 4
