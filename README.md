# 區塊鏈眾包感知系統

這個項目實現了一個基於區塊鏈的眾包感知系統，用於分散式任務的發布、執行和驗證。系統通過使用激勵機制（R-coin和S-coin）來促進參與者間的公平合作。

## 系統架構

本系統主要由以下角色和組件組成：

### 角色
- **Requester (請求者)**: 發布任務並提供獎勵的實體
- **Worker (工作者)**: 執行任務並獲取獎勵的實體
- **Verifier (驗證者)**: 從Worker中選出，負責驗證任務執行的品質

### 組件
- **區塊鏈**: 記錄所有交易和評估結果
- **Server**: 負責廣播任務和選擇驗證者
- **QualityReputationManager**: 評估任務完成度並更新聲譽

### 代幣系統
- **R-coin**: 資源代幣，用於發布任務和獲取獎勵
- **S-coin**: 聲譽代幣，影響被選為驗證者的概率

## 目錄結構

```
├── src/                  # 源代碼目錄
│   ├── models/           # 數據模型
│   │   ├── node.py       # 基礎節點類
│   │   ├── worker.py     # 工作者類
│   │   └── requester.py  # 請求者類
│   ├── services/         # 服務類
│   │   ├── server.py     # 服務器類
│   │   └── quality_reputation_manager.py # 質量聲譽管理器
│   ├── blockchain/       # 區塊鏈相關
│   │   ├── block.py      # 區塊類
│   │   └── blockchain.py # 區塊鏈類
│   ├── config/           # 配置
│   │   ├── system_config.py # 系統配置
│   │   └── logging_config.py # 日誌配置
│   ├── utils/            # 工具函數
│   │   ├── crypto.py     # 加密工具
│   │   └── simulation_utils.py # 模擬工具
│   └── simulation/       # 模擬相關
│       ├── simulator.py  # 模擬器
│       └── main.py       # 主程序
├── run.py                # 啟動腳本
└── README.md             # 本文檔
```

## 安裝說明

1. 確保您已安裝 Python 3.7 或更高版本。

2. 克隆此倉庫：
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

3. （可選）建立虛擬環境：
   ```
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
   ```

4. 安裝依賴：
   ```
   pip install -r requirements.txt  # 如果有requirements.txt文件
   ```

## 使用方法

運行模擬：
```
python run.py
```

程序會模擬多輪的眾包感知過程，包括：
1. 請求者創建任務並設置獎勵
2. 服務器廣播任務
3. 選擇驗證者
4. 工作者提交任務結果
5. 評估任務完成度
6. 更新聲譽和獎勵
7. 創建新區塊記錄交易

## 系統流程

1. **任務創建**：Requester創建任務，設定獎勵金額，並從其R-coin中扣除相應金額。

2. **廣播任務**：Server將任務廣播給所有Worker。

3. **選擇驗證者**：
   - 每個Worker宣告部分R-coin參與驗證者競選
   - 基於宣告的R-coin和現有的S-coin，計算被選為驗證者的概率
   - 選擇一個驗證者

4. **任務執行與提交**：所有Worker執行任務並提交結果。

5. **評估與獎勵**：
   - 評估每個Worker的任務完成度
   - 根據完成度給予獎勵或懲罰
   - 驗證者獲得額外獎勵

6. **區塊創建**：將所有記錄添加到區塊鏈中，創建新區塊。

## 輸出結果

運行完成後，系統會生成以下文件：
- `blockchain.json`：區塊鏈數據
- `workers_state.json`：工作者狀態
- `requester_state.json`：請求者狀態

## 擴展功能

本系統可以進一步擴展，例如：
- 增加多個請求者
- 實現更複雜的任務分配策略
- 增加更多的獎勵機制
- 實現實際的感知任務處理邏輯

## 許可證

[這裡添加適當的許可證信息] 