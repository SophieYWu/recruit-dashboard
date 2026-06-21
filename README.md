# 集團招募主儀表板 — 自動更新公開網頁

每天自動向 Notion 抓最新資料，產生一個可對外分享的網頁。
免費、不需自己的伺服器，用 **GitHub Actions（每日排程）＋ GitHub Pages（公開託管）**。

---

## 運作原理（三個環節）

```
① 抓資料            ② 排程              ③ 公開託管
build.py  ──每天──▶  GitHub Actions  ──▶  GitHub Pages
(查 Notion API)      (cron 自動跑)        (公開網址)
   │                                         ▲
   └── 重算後寫出 data.json ──── index.html 載入時讀取 ──┘
```

- `build.py`：呼叫 Notion API 撈「集團招募主儀表板」與「第一階段面試表」，重算後覆蓋 `data.json`。
- `index.html`：網頁，載入時讀 `data.json` 畫出 KPI 與兩張圖。
- `.github/workflows/update.yml`：每週一台灣時間 06:00 自動執行 `build.py` 並更新網站。

> 只輸出「彙總數字」（總職缺、完成、待招募、各部門人數），**不含任何姓名、薪資、評語**，所以適合對外分享。

---

## 部署步驟（約 30 分鐘，做一次即可）

### 1. 建立 Notion 整合金鑰
1. 到 <https://www.notion.so/my-integrations> →「New integration」→ 命名（如 `招募儀表板`）→ 取得 **Internal Integration Token**（`ntn_...` 或 `secret_...`）。
2. 在 Notion 打開這兩個資料庫，右上「⋯」→「Connections / 連線」→ 加入剛建立的整合：
   - 📌 集團招募主儀表板
   - 📞 第一階段 初步訪談評估表

### 2. 建立 GitHub repo 並上傳本資料夾
把本資料夾全部檔案（`build.py`、`index.html`、`data.json`、`requirements.txt`、`.github/`）放到一個新的 GitHub repo。

### 3. 設定金鑰
repo →「Settings」→「Secrets and variables」→「Actions」→「New repository secret」：
- Name：`NOTION_TOKEN`
- Value：步驟 1 的金鑰

### 4. 開啟 GitHub Pages
repo →「Settings」→「Pages」→ Source 選「Deploy from a branch」→ Branch 選 `main`、資料夾 `/ (root)` → Save。
幾分鐘後會得到公開網址：`https://<你的帳號>.github.io/<repo 名稱>/`

### 5. 測試自動更新
repo →「Actions」→ 選「Update dashboard」→「Run workflow」手動跑一次。
成功後 `data.json` 會被更新、網頁即顯示最新數字。之後每天 06:00 自動執行。

---

## 日常維護

- **改更新時間**：編輯 `update.yml` 的 `cron`（用 UTC，台灣＝UTC＋8）。
- **更新在職人數**：人事異動時，改 `build.py` 最上方的 `HEADCOUNT`。
  （在職名冊是手寫表格，不適合每日自動解析；若要全自動，可在 Notion 另建一個「部門／在職人數」結構化資料庫，再改 `build.py` 改抓它。）
- **改人才庫口徑**：目前以「有訪談日期」為準；要改成「安排面試✓」或「穩定度＝穩定」，調整 `build.py` 第 2 段的判斷即可。

---

## 對外公開的提醒

- GitHub Pages 是**完全公開**的，任何人有網址都能看。本頁只含彙總數字已做去識別化。
- 若希望**限定對象**（只給特定外部夥伴），可改用：
  - **Cloudflare Pages ＋ Cloudflare Access**：免費，可用 Email 驗證才放行。
  - **Netlify**：付費方案可設密碼保護。
- 正式對外前，建議仍向主管確認招募/人數彙總數字可公開的範圍。

---

## 替代部署（擇一即可）
GitHub Pages 之外，`build.py` ＋ `index.html` 同樣可放到 **Vercel / Netlify / Cloudflare Pages**，
用各平台的「Scheduled Function / Cron」每天觸發 `build.py`，原理相同。
