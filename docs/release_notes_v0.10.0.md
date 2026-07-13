# RollSlope Quant MVP — Release Notes v0.10.0

- **版本號**：v0.10.0
- **commit hash**：997c1103dbac2da2e65d9aef259401c2d9ebd0fb
- **雲端網址**：https://rollslope-quant-mvp.streamlit.app/

## 已完成功能摘要

1. Demo 範例模式：內建「先急跌、再盤整、後急漲」範例資料，一鍵計算
2. 手動 X/Y 輸入模式：直接在網頁表格編輯數值計算
3. 通用 CSV 上傳模式：手動選擇 X 欄位、Y 欄位
4. 市場 K 線 CSV 上傳模式：自動辨識 datetime / close 欄位
5. datetime 自動排序：上傳的市場 K 線資料若時間順序錯亂會自動依時間升冪排序
6. close 欄位驗證：缺欄、空白、無法轉數字、數值全部相同都會有清楚的中文錯誤提示
7. rolling slope table：輸出 t1/t2/t3、z1/z2/z3、breakpoint_1/breakpoint_2、r_squared 等欄位
8. 最後一個 window 圖表：顯示原始資料、三段分段擬合線與轉折點
9. Streamlit Cloud 部署：手機瀏覽器可直接連線使用，不需要同一個 Wi-Fi、不需要開本機電腦

## 測試狀態

- `pytest` 全數通過（本版本封裝前為 209 項測試通過；本次封裝流程另新增靜態測試）
- 所有測試皆為本機/CI 可重複執行，不連網、不需要券商憑證

## 已知限制

本工具僅供研究與模型計算使用：

- 不連接任何券商
- 不會下單
- 不放任何金鑰或密鑰
- 不涉及買賣
- 不操作真實資金

畫面上看到的所有結果僅供研究參考，不構成任何投資建議。
