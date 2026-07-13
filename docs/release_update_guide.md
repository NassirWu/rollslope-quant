# RollSlope Quant MVP — 雲端版更新流程說明

給要「上新版本」的人看，不談程式架構，只說步驟。

## 更新流程（四步驟）

1. **修改版本號**
   打開 `src/rollslope_quant/interfaces/web/version.py`，把 `CLOUD_APP_VERSION` 改成新的版本字串，例如從 `v0.9.8` 改成 `v0.9.9`。

2. **跑測試**
   在專案資料夾裡執行：
   ```
   .venv\Scripts\python.exe -m pytest -q
   ```
   全部測試都要通過（顯示 `passed`，沒有 `failed`）才能繼續下一步。

3. **commit**
   把修改的內容提交到版本紀錄（commit）。

4. **push**
   把 commit 推送（push）到 GitHub。推送完成後，Streamlit Cloud 會自動偵測到更新並重新部署，不需要手動操作 Streamlit Cloud 的介面。重新部署通常需要等待數分鐘。

## 特別提醒

- 更新版本時，**不要**在 Streamlit Cloud 的 Secrets 欄位填任何東西。本專案雲端版本不需要任何金鑰或密鑰設定。
- 本工具只做斜率模型計算，不連接任何券商，不會下單，不會操作真實資金，不涉及買賣。
- 如果需要新增雲端版的相依套件（`cloud/requirements.txt`），必須先在本機用同一份檔案重新建立虛擬環境並確認能安裝成功，再推送到 GitHub，避免 Streamlit Cloud 建置失敗。
- 每次更新前建議先對照 `docs/cloud_release_checklist.md` 逐項確認。
