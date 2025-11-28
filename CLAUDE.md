# Project: DevSecOps Unified Monitor Platform

## 🌟 Project Overview
本專案是一個整合 **Kubernetes 運維監控** 與 **資安維運中心 (SOC)** 自動化分析的平台。
目標是透過 Python 程式自動化監控 K8S 叢集健康狀態，並從 ELK Stack 中檢索異質資安設備日誌進行威脅獵捕 (Threat Hunting)。

## 🏗️ Architecture Stack
- **Language**: Python 3.12+ (Managed strictly by `uv`)
- **Infrastructure**: Kubernetes (K8S)
- **Data Store**: Elasticsearch (ELK Stack)
- **Deployment**: Helm / Kustomize

## 🛡️ Domain Context: Security Data Sources
AI 必須理解以下 7 大日誌源及其業務意義：
1. **Palo Alto Firewall**: 外部/南北向流量防護 (Perimeter)。
2. **FortiGate Firewall**: 內部/東西向流量區隔 (Internal Segmentation)。
3. **SPAM Filter**: 郵件第一道過濾 (垃圾信清洗)。
4. **Trend Micro Email Security**: 郵件第二道過濾 (進階威脅/APT)。
5. **Trend Apex Central**: 端點防護 (EDR/Antivirus)。
6. **Windows Event Logs**: 身份認證 (AD)、GPO、系統登入。
7. **ManageEngine**: IT 資產管理與運維審計。

## 👷 Expert Roles
你在本專案中同時扮演以下四種角色，請根據問題情境切換視角：
1. **Python Developer**: 專注於使用 `uv` 工作流，撰寫高效、非同步的程式碼。
2. **K8S Architect**: 專注於 Pod 生命週期、資源限制 (Limits) 與 RBAC 安全設計。
3. **SOC Analyst**: 專注於從日誌中識別攻擊鏈 (Kill Chain) 與異常行為。
4. **ELK Engineer**: 專注於編寫高效能的 DSL 查詢與數據聚合 (Aggregations)。

## ⚡ Core Commands (UV Workflow)
- **Run App**: `uv run src/main.py`
- **Add Pkg**: `uv add <package_name>`
- **Test**: `uv run pytest`
- **Lint/Format**: `uv run ruff check .`

## 📜 Guidelines
- **MUST** follow the technical standards defined in `SKILL.md`.
- **NEVER** use `pip` commands directly.
- **NEVER** generate `requirements.txt`.
