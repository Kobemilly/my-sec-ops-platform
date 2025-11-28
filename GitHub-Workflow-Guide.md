# GitHub 工作流程指南

## 📊 工作流程示意圖

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub 協作開發流程                           │
└─────────────────────────────────────────────────────────────────────┘

    [main/master 分支]
         │
         ├─── git checkout -b feature/new-feature
         │
    [feature 分支] ←─── 在這裡開發新功能
         │
         ├─── git add . && git commit -m "commit message"
         │
         ├─── git push -u origin feature/new-feature
         │
    [GitHub 上的 PR] ←─── gh pr create
         │
         ├─── 代碼審查 & 測試
         │
         ├─── gh pr merge (合併)
         │
    [main/master 分支] ←─── 功能合併完成
         │
         └─── git pull origin main (同步最新代碼)
```

## 🛠️ 詳細指令步驟

### 步驟 1: 創建功能分支
```bash
# 確保在主分支上且是最新版本
git checkout main
git pull origin main

# 創建並切換到新的功能分支
git checkout -b feature/add-user-login
```

### 步驟 2: 開發功能
```bash
# 編輯文件，添加新功能...
# 例如：創建一個新文件
echo "def login(): pass" > src/auth.py

# 修改現有文件
# vim src/main.py
```

### 步驟 3: 提交變更
```bash
# 查看變更狀態
git status

# 添加變更到暫存區
git add .
# 或者選擇性添加
git add src/auth.py src/main.py

# 提交變更
git commit -m "✨ Feature: Add user login functionality

- Add login authentication system
- Update main.py with login integration
- Add security validations

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 步驟 4: 推送到 GitHub
```bash
# 推送功能分支到 GitHub
git push -u origin feature/add-user-login
```

### 步驟 5: 創建 Pull Request
```bash
# 使用 GitHub CLI 創建 PR
gh pr create \
  --title "✨ Feature: Add user login functionality" \
  --body "## 🚀 功能描述
- 新增用戶登入系統
- 添加安全驗證機制
- 更新主要應用集成

## 📋 測試清單
- [x] 登入功能正常運作
- [x] 安全驗證通過
- [x] 無破壞性變更

請審查並合併 🔍"
```

### 步驟 6: 審查與合併
```bash
# 查看所有 PR
gh pr list

# 查看特定 PR 詳情
gh pr view 1

# 查看 PR 的變更內容
gh pr diff 1

# 如果滿意，合併 PR
gh pr merge 1 --squash --delete-branch
```

### 步驟 7: 同步最新變更
```bash
# 切換回主分支
git checkout main

# 同步遠程最新變更
git pull origin main

# 清理本地已合併的分支
git branch -d feature/add-user-login
```

## 🎯 實際範例演示

讓我們用一個具體的例子：**為 SOC 平台添加黑暗模式切換功能**

### 範例 1: 添加黑暗模式功能

```bash
# 1. 創建功能分支
git checkout -b feature/dark-mode-toggle

# 2. 創建切換按鈕的 HTML 組件
cat << 'EOF' > templates/components/dark_mode_toggle.html
<div class="form-check form-switch">
  <input class="form-check-input" type="checkbox" id="darkModeToggle" checked>
  <label class="form-check-label" for="darkModeToggle">
    <i class="fas fa-moon me-1"></i>暗色模式
  </label>
</div>
EOF

# 3. 添加 JavaScript 功能
cat << 'EOF' > static/js/dark-mode.js
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const body = document.body;

    toggle.addEventListener('change', function() {
        if (this.checked) {
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        }
    });
}

document.addEventListener('DOMContentLoaded', initDarkMode);
EOF

# 4. 提交變更
git add .
git commit -m "✨ Feature: Add dark mode toggle functionality

- Add dark mode toggle component
- Implement JavaScript theme switching
- Add localStorage persistence for user preference
- Enhance user interface customization options

Improves accessibility and user experience.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. 推送並創建 PR
git push -u origin feature/dark-mode-toggle

gh pr create \
  --title "✨ Feature: Add dark mode toggle" \
  --body "## 🌙 功能描述
新增暗色模式切換功能，提升用戶體驗

### ✨ 新增內容:
- 暗色模式切換按鈕
- JavaScript 主題切換邏輯
- localStorage 儲存用戶偏好
- 響應式主題變更

### 🎯 效益:
- 提升可訪問性
- 改善在暗環境下的使用體驗
- 現代化的 UI/UX 設計

### 🧪 測試:
- [x] 切換功能正常運作
- [x] 主題偏好持久化儲存
- [x] 響應式設計保持一致

準備審查與合併! 🚀"
```

### 範例 2: 修復 Bug

```bash
# 1. 創建修復分支
git checkout -b bugfix/elasticsearch-connection-timeout

# 2. 修復超時問題
# 編輯 src/security/elasticsearch_client.py
# 添加連接超時配置...

# 3. 提交修復
git add src/security/elasticsearch_client.py
git commit -m "🐛 Fix: Resolve Elasticsearch connection timeout issues

- Increase connection timeout to 30 seconds
- Add retry logic for failed connections
- Improve error handling for network issues
- Add connection status logging

Fixes issue #5 - Elasticsearch connection failures in slow networks.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. 推送並創建修復 PR
git push -u origin bugfix/elasticsearch-connection-timeout

gh pr create \
  --title "🐛 Fix: Elasticsearch connection timeout" \
  --body "## 🔧 Bug 修復
解決 Elasticsearch 連接超時問題

### 🐛 問題描述:
- 在慢網路環境下連接失敗
- 缺乏重試機制
- 錯誤訊息不清楚

### ✅ 修復內容:
- 增加連接超時時間至 30 秒
- 添加自動重試邏輯
- 改善錯誤處理與日誌記錄

### 🧪 測試:
- [x] 慢網路環境測試通過
- [x] 錯誤恢復機制正常
- [x] 日誌記錄詳細完整

Closes #5"
```

## 📋 常用指令速查表

### Git 基本操作
```bash
# 查看狀態
git status

# 查看分支
git branch -a

# 切換分支
git checkout branch-name

# 創建並切換分支
git checkout -b new-branch-name

# 刪除分支
git branch -d branch-name
```

### GitHub CLI 操作
```bash
# 查看 PR 列表
gh pr list

# 創建 PR
gh pr create

# 合併 PR
gh pr merge PR-NUMBER

# 查看 PR 詳情
gh pr view PR-NUMBER

# 查看倉庫資訊
gh repo view

# 創建 Issue
gh issue create

# 查看 Issues
gh issue list
```

### 協作同步
```bash
# 同步遠程變更
git fetch origin

# 合併遠程變更
git pull origin main

# 推送本地變更
git push origin branch-name

# 強制推送 (謹慎使用)
git push --force-with-lease origin branch-name
```

## ⚠️ 最佳實踐提醒

### ✅ 做這些:
- 為每個功能/修復創建獨立分支
- 寫清楚的提交訊息
- 在 PR 中詳細描述變更
- 定期同步主分支的最新變更

### ❌ 避免這些:
- 直接在 main/master 分支上開發
- 提交訊息過於簡略
- 一個 PR 包含多個不相關功能
- 長期不同步主分支變更

## 🎯 總結

**GitHub 工作流程核心**:
分支開發 → 提交變更 → 推送分支 → 創建 PR → 審查合併 → 同步主分支

這個流程確保：
- 代碼品質與穩定性
- 團隊協作效率
- 變更歷史追蹤
- 功能獨立開發