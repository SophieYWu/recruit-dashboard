# -*- coding: utf-8 -*-
"""
每天向 Notion API 重抓招募與第一階段面試資料，重算後寫出 data.json。
網頁 (index.html) 載入時讀取 data.json，達成自動更新。
需要環境變數 NOTION_TOKEN（Notion 內部整合金鑰）。
"""
import os, json, datetime, requests

NOTION_TOKEN   = os.environ["NOTION_TOKEN"]
NOTION_VERSION = "2025-09-03"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# 兩個資料來源（Data Source ID）
JOBS_DS = "30632fab-3664-81f1-b5ab-000bbc2abd23"   # 📌 集團招募主儀表板
CAND_DS = "30632fab-3664-81b9-8c71-000b28fba3d9"   # 📞 第一階段 初步訪談評估表

# 各部門在職人數（含近期將報到者；人事異動時改這裡即可）
HEADCOUNT = {
    "投資創新事業": 10,
    "會展與專案部": 13,
    "品牌與認證部": 11,
    "數位開發處":   8,
    "財務行政中心": 7,
}
# 部門顯示順序（三張圖共用，方便對照）
CANON = ["品牌與認證部", "會展與專案部", "投資創新事業", "財務行政中心", "數位開發處"]


def query_all(ds_id):
    """分頁撈出一個 data source 的所有列。"""
    url = f"https://api.notion.com/v1/data_sources/{ds_id}/query"
    results, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(url, headers=HEADERS, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        results += data["results"]
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return results


def _p(page, name):
    return page["properties"].get(name)

def select_name(pr):
    if not pr:
        return None
    v = pr.get("select") or pr.get("status")
    return v["name"] if v else None

def title_text(pr):
    if not pr:
        return ""
    return "".join(x.get("plain_text", "") for x in pr.get("title", [])).strip()

def relation_ids(pr):
    if not pr:
        return []
    return [x["id"].replace("-", "") for x in pr.get("relation", [])]

def date_start(pr):
    if not pr:
        return None
    d = pr.get("date")
    return d.get("start") if d else None


def main():
    # ---- 1) 職缺：算總職缺 / 完成 / 待招募，並統計各部門待招募 ----
    jobs = query_all(JOBS_DS)
    job_dept = {}
    openings = {d: 0 for d in CANON}   # 各部門待招募（未到職）職缺數
    total = done = 0
    for j in jobs:
        title = title_text(_p(j, "招聘職務"))
        if not title or title == "-":
            continue  # 跳過空白待建立列
        dept  = select_name(_p(j, "所屬部門"))
        stage = select_name(_p(j, "狀態"))
        job_dept[j["id"].replace("-", "")] = dept
        total += 1
        if stage == "到職":
            done += 1
        elif dept in openings:
            openings[dept] += 1   # 未到職 = 仍在招募中
    wait = total - done

    # ---- 2) 人才庫：第一階段面試表中「有訪談日期」者，依職缺對應部門 ----
    cands = query_all(CAND_DS)
    talent = {d: 0 for d in CANON}
    for c in cands:
        if not date_start(_p(c, "訪談日期")):
            continue  # 沒有訪談日期 = 尚未實際完成第一階段面試，不計入
        dept = None
        for jid in relation_ids(_p(c, "職缺連結")):
            if job_dept.get(jid) in talent:
                dept = job_dept[jid]
                break
        if dept:
            talent[dept] += 1

    out = {
        "snapshot":  datetime.date.today().isoformat(),
        "kpi":       {"total": total, "done": done, "wait": wait},
        "depts":     CANON,
        "headcount": [HEADCOUNT[d] for d in CANON],
        "openings":  [openings[d]  for d in CANON],
        "talent":    [talent[d]    for d in CANON],
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("data.json 已更新：", json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
