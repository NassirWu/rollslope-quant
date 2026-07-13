# RollSlope Quant MVP — Release 封裝流程說明

給要「打包出貨」的人看，說明怎麼用 `scripts/package_release.ps1` 產生一份完整的交付包。

## 事前準備：放入兩份 Word 說明檔

在執行封裝腳本之前，必須先手動把兩份 Word 檔放到 `release_inputs/word/` 資料夾底下：

- `RollSlope_Quant_MVP_完全新手操作說明_v0.10.0.docx`
- `RollSlope_Quant_MVP_專業技術交付說明_v0.10.0.docx`

這兩份 Word 檔**不會**進版本控制（Git），需要每次出貨前自行準備或更新內容後放進這個資料夾。`release_inputs/word/.gitkeep` 只是用來讓資料夾結構保留在版本控制裡，不代表 Word 檔本身有被追蹤。

## 如何執行封裝腳本

在專案根目錄用 PowerShell 執行：

```
.\scripts\package_release.ps1
```

預設會使用：
- 版本號：`v0.10.0`
- 來源版本（SourceRef）：`HEAD`（目前 checkout 的內容）
- 兩份 Word 檔：上面提到的預設路徑

也可以自訂參數，例如：

```
.\scripts\package_release.ps1 -Version "v0.10.1" -SourceRef "v0.10.1"
```

## 產出檔案在哪裡

執行完成後，所有產出都會放在專案根目錄的 `release/` 資料夾裡：

- `RollSlope_Quant_MVP_v0.10.0_Source.zip`：純原始碼快照（只包含 Git 有追蹤的檔案，不含金鑰、不含本機環境檔）
- 兩份 Word 說明檔的複本
- `release_notes_v0.10.0.md` 的複本
- `RollSlope_Quant_MVP_v0.10.0_Delivery.zip`：把以上所有檔案打包成的最終交付包

`release/` 資料夾本身不會進 Git，每次執行都會先清空重建，確保產出是乾淨的。

## 常見錯誤

- **找不到 Word 檔**：請確認兩份 Word 檔的檔名與路徑跟 `release_inputs/word/` 底下的完全一致，檔名有打錯字或版本號不符都會找不到。
- **找不到 release notes**：請確認 `docs/release_notes_v<版本號>.md` 這份檔案已經存在，版本號要跟執行腳本時的 `-Version` 參數一致。
- **source ref 不存在**：如果自訂了 `-SourceRef`，要確認那是一個真的存在的 Git 版本（例如 commit hash、tag 或分支名稱），打錯字或版本還沒建立都會失敗。

## 風控提醒

打包出來的交付包只包含本工具的斜率模型計算功能，不連接任何券商、不會下單、不放任何金鑰、不涉及買賣，僅供研究參考。
