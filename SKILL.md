# Technical Skills & Best Practices

## 🐍 Python Development (Modern uv Workflow)
**Core Principle**: 使用 `uv` 作為唯一套件管理工具。

### UV Commands Mapping
| Action | Command | Note |
| :--- | :--- | :--- |
| Init Project | `uv init` | 專案初始化 |
| Add Dependency | `uv add <pkg>` | 禁止使用 pip install |
| Add Dev Tool | `uv add --dev <pkg>` | 如 pytest, ruff |
| Run Script | `uv run <script>` | 自動使用虛擬環境 |
| Sync Environment | `uv sync` | 還原專案環境 |

### Coding Standards
- **Type Hinting**: 所有函數必須包含 Type Hints。
- **Async First**: 涉及 I/O (K8S API, ELK Query) 操作優先使用 `async/await`。
- **Config**: 使用 `pydantic-settings` 讀取環境變數。

---

## ☸️ Kubernetes (K8S) & DevOps
**Core Principle**: 宣告式管理、資源隔離、最小權限。

### Deployment Standards
1. **Resources**: 所有 Pod **必須**設定 `resources.requests` 和 `limits`。
2. **Liveness/Readiness**: 必須配置 Probe 以確保服務可用性。
3. **Namespace**: 應用程式需部署於獨立 Namespace，嚴禁使用 `default`。

### Python K8S Implementation
- **SDK**: 使用 `uv add kubernetes` (同步) 或 `uv add kubernetes-asyncio` (非同步)。
- **Config Loading**:
  ```python
  try:
      config.load_incluster_config() # In-Cluster
  except config.ConfigException:
      config.load_kube_config()    # Local Dev
🦅 Cybersecurity & ELK Analytics
Core Principle: 精確查詢、時區統一、跨設備關聯。
ELK Query Standards (Python)
SDK: 使用 uv add elasticsearch。
Performance:
禁止使用 size: 10000 進行深頁查詢，必須使用 search_after 或 scroll。
查詢時務必指定 _source 欄位，減少網路傳輸。
Timezone: 讀取後立即轉為 UTC 處理，輸出時轉為 Asia/Taipei。
Data Source Specifics (Log Logic)
Firewalls (Network):
Correlation: 關聯 Palo Alto (Ext) 與 FortiGate (Int) 需考慮 NAT 轉換。
Fields: 統一映射至 source.ip, destination.port, network.transport。
Email Security:
Trace: 使用 Message-ID 或 Subject + Sender 作為跨 SPAM/Trend Micro 的關聯鍵。
Alert: 若 SPAM 放行但 Trend Micro 阻擋，視為高風險特徵。
Endpoint & System:
Windows: 監控 Event ID 4624 (Login), 4625 (Fail), 4740 (Lockout)。
Apex Central: 關注 Virus/Malware 事件與 Windows 4688 (Process Create) 的關聯。
