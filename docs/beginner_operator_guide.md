# RollSlope Quant MVP — 非技術人員一鍵操作說明

## 1. 這個工具是做什麼的？

- 把一串數字資料切成三段趨勢
- 算出 t1 / t2 / t3
- 同時輸出 z1 / z2 / z3
- z1 = t1，z2 = t2，z3 = t3

## 2. 這個版本不會做什麼？

- 不會買賣
- 不會自動下單
- 不會操作真實資金
- 不會連接券商
- 不需要 Ollama
- 不需要金鑰
- 不需要券商憑證
- 不需要任何交易帳號設定

## 3. 只想看範例結果怎麼做？

1. 雙擊 `run_demo.bat`
2. 等黑色視窗顯示完成
3. 打開 `reports` 資料夾
4. 查看 `rolling_slope_table.csv` 和兩張圖

## 4. 想自己輸入 X/Y 怎麼做？

1. 第一次雙擊 `run_manual_xy.bat`
2. 系統會建立 `data/raw/manual_xy_template.csv`
3. 用 Excel 打開 `manual_xy_template.csv`
4. 修改 x,y 數字
5. 存檔
6. 再雙擊 `run_manual_xy.bat`
7. 打開 `reports/manual_xy_result.csv`

## 5. X 是什麼？

- X 是橫軸
- 可以是時間順序、K 線序號、資料順序
- 例如 1,2,3,4,5

## 6. Y 是什麼？

- Y 是你要分析的數值
- 在股票裡通常是收盤價 close
- 也可以是你手上任何要分析的數值

## 7. 怎麼看結果？

- t1：第一段斜率
- t2：第二段斜率
- t3：第三段斜率
- z1 / z2 / z3：等同 t1 / t2 / t3
- r_squared：模型擬合品質
- is_valid：是否通過品質門檻

## 8. 常見錯誤與處理方式

- 黑色視窗說找不到 Python
- CSV 欄位名稱錯誤
- 資料不足 6 筆
- Excel 沒有關閉導致檔案被鎖住
- 輸出檔打不開

## 9. 給操作者的最短流程

**情境 A：看範例**
雙擊 `run_demo.bat` → 打開 `reports`

**情境 B：自己填 X/Y**
雙擊 `run_manual_xy.bat` → 填 CSV → 再雙擊 `run_manual_xy.bat` → 打開 `reports/manual_xy_result.csv`
