# 簡易PTT八卦板爬蟲
## USAGE
* PAGE_COUNT: 設定要爬取的頁數
* 直接執行main.py
## 資料儲存
* db: Sqlite
* 爬取結果儲存於db/mydb.db中
* 推文表: __pttpost__

  | 欄位名稱 | 型態    | 說明 |
  | ------- | ------- | -------- |
  | id      | INTEGER | 發文編號  |
  | board   | TEXT    | 看板      |
  | code    | TEXT    | 發文識別碼 |
  | author  | TEXT    | 作者      |
  | title   | TEXT    | 標題      |
  | dt      | TEXT    | 日期時間  |
  | content | TEXT    | 發文內容  |
* 回文表: __pttpush__

  | 欄位名稱    | 型態    | 說明 |
  | ---------- | ------- | ------------- |
  | pttpost_id | INTEGER | 對應之發文編號 |
  | user       | TEXT    | 推文者        |
  | ipdt       | TEXT    | ip & 日期時間 |
  | tag        | TEXT    | 推文分類      |
  | content    | TEXT    | 推文內容      |