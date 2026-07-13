# RollSlope Quant 版本動態日誌

## v0.10.0-R — Release Packaging & Cleanup
狀態：已完成
類型：封裝流程 / 交付流程
重點：
- 新增正式 release 封裝流程
- 新增 scripts/package_release.ps1
- 新增 release notes
- 新增 release packaging guide
- 新增 release_inputs/word/ 作為 Word 說明檔暫存位置
- 產生正式交付包：
  - RollSlope_Quant_MVP_v0.10.0_Source.zip
  - RollSlope_Quant_MVP_v0.10.0_Delivery.zip
- 交付包內含：
  - 原始碼 zip
  - 完全新手操作說明 Word
  - 專業技術交付說明 Word
  - release notes
- 自動清除舊封裝輸出、reports 產物、data/raw sample 產物
- Word 檔與 release 輸出不進 Git
- CLOUD_APP_VERSION 修正為 v0.10.0

測試：
- pytest：224 passed

備註：
- 此階段不新增交易功能
- 此階段不連券商、不下單、不放金鑰、不操作真實資金

---

## v0.10.0 — Market K-line CSV Import
狀態：已完成
類型：資料匯入 / 雲端功能
穩定 commit：
997c110 Add market K-line CSV import with datetime auto-sort and close validation

重點：
- 新增「上傳市場 K 線 CSV」模式
- 支援欄位：
  - datetime
  - open
  - high
  - low
  - close
  - volume
- close 欄位自動辨識與驗證
- datetime 欄位自動辨識與升冪排序
- 若無 datetime，使用資料列順序作為 X
- 新增 market K 線 CSV 模板
- 新增 sample market K-line CSV 產生腳本
- 新增市場 CSV 操作文件
- 最後 rolling window 圖表可正常顯示

測試：
- pytest：209 passed

雲端：
- Streamlit Cloud 已同步更新
- 雲端網址：
  https://rollslope-quant-mvp.streamlit.app/

備註：
- 此階段只做資料上傳、模型計算與圖表顯示
- 不連券商、不下單、不放金鑰

---

## v0.9.9 — Cloud Result Visualization
狀態：已完成
類型：雲端視覺化
穩定 commit：
0b10e84 Add cloud result visualization with last-window slope fit chart

重點：
- 雲端計算結果新增圖表
- 顯示最後一個 rolling window 的三段分段線性擬合
- 圖表包含：
  - 原始資料點
  - 三段擬合線
  - breakpoints
  - t1 / t2 / t3
  - R²
- Demo、手動 X/Y、通用 CSV 三模式皆支援圖表
- 圖表失敗時不影響表格顯示

測試：
- pytest：183 passed

---

## v0.9.8 — Cloud Release Hardening
狀態：已完成
類型：雲端發版強化
穩定 commit：
66c87ce Add cloud release version display and release documentation

重點：
- 新增雲端版本號顯示
- 新增使用說明區塊
- 新增結果解讀區塊
- 新增 release update guide
- 新增 cloud release checklist
- 改善非技術使用者操作體驗

測試：
- pytest：175 passed

---

## v0.9.7 — Streamlit Cloud Deployment
狀態：已完成
類型：雲端部署
穩定 commit：
f7dca86 Add Streamlit Cloud deployment package

重點：
- 新增 cloud/app.py
- 新增 cloud/requirements.txt
- 新增 Streamlit Cloud 部署設定
- 雲端可由手機直接開啟使用
- 不需要本機電腦開服務
- 不需要同 Wi-Fi

測試：
- pytest：161 passed

雲端網址：
https://rollslope-quant-mvp.streamlit.app/

---

## v0.9.6 — Mobile Web Operator Interface
狀態：已完成
類型：本機手機網頁版
穩定 commit：
308483f Add mobile web operator interface

重點：
- 新增 Streamlit 本機手機操作介面
- 支援 Demo 範例模式
- 支援手動 X/Y 輸入
- 支援通用 CSV 上傳
- 新增 run_mobile_web.bat
- 手機可在同 Wi-Fi 下使用 Network URL 操作

測試：
- pytest：147 passed

---

## v0.9.x Earlier MVP Foundation
狀態：已完成
類型：核心模型 / 匯出 / 視覺化基礎

重點：
- 建立三段分段線性擬合核心
- 實作 calculate_dynamic_slopes()
- 輸出 t1 / t2 / t3
- 輸出 breakpoints
- 計算 R²
- 新增 rolling slope table
- 新增 CSV 匯出
- 新增 V 轉與倒 V demo
- 新增本機測試腳本
- 新增基礎文件

核心原則：
- 模型先行
- 資料先行
- 先研究、後執行
- 不連券商、不下單、不放金鑰

---

## 目前最新穩定狀態

目前正式穩定版本：
v0.10.0

目前正式交付包：
release/RollSlope_Quant_MVP_v0.10.0_Delivery.zip

目前雲端網址：
https://rollslope-quant-mvp.streamlit.app/

目前功能：
- Demo 範例模式
- 手動 X/Y 輸入
- 通用 CSV 上傳
- 市場 K 線 CSV 上傳
- datetime 自動排序
- close 欄位驗證
- rolling slope table
- 最後一個 window 圖表
- Word 使用說明
- Source zip
- Delivery zip
- release notes
- 自動封裝腳本

目前限制：
- 不連券商
- 不下單
- 不放金鑰
- 不做真實資金操作
- 僅作模型研究、資料分析與系統架構驗證
