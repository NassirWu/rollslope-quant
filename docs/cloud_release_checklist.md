# RollSlope Quant MVP — 雲端版上版檢查清單

每次要把新版本推送到 Streamlit Cloud 之前，請逐項確認打勾。

## 上版前檢查

- [ ] `src/rollslope_quant/interfaces/web/version.py` 裡的版本字串已經更新
- [ ] 已執行 `.venv\Scripts\python.exe -m pytest -q`，全部測試通過
- [ ] `docs/cloud_operator_guide.md` 的內容如果有變動，已經同步更新
- [ ] 沒有修改以下計算邏輯相關檔案：
  - `calculate_dynamic_slopes()`
  - `rolling_slope_table.py`
  - `export_rolling_slope_table.py`
  - `slope_visualizer.py`
- [ ] 沒有修改券商相關模組、風控模組、Plutus 模組、tools/ai_advisors 模組
- [ ] `cloud/requirements.txt` 沒有非必要的變動
- [ ] `run_demo.bat`、`run_manual_xy.bat`、`run_mobile_web.bat` 三支本機腳本都能正常執行
- [ ] `git status` 顯示乾淨，所有變更都已經 commit
- [ ] 已經把 commit 推送（push）到 GitHub

## 上版後檢查

- [ ] 等待 Streamlit Cloud 自動重新部署完成
- [ ] 打開雲端網址，確認畫面正常顯示，版本號已經更新成新的版本
- [ ] 確認 Streamlit Cloud 的 Secrets 欄位仍然保持空白
- [ ] 確認本工具仍然只做斜率模型計算：不連接券商、不會下單、不涉及買賣、不操作真實資金
