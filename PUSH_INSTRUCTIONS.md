# 推送代码到 GitHub - 最终方案

## 问题：HTTP 413 错误

推送大小超过 GitHub 限制（~100MB），已创建干净分支解决。

## 解决方案：使用干净分支

已创建新分支 `temp-main`，包含所有代码但无历史记录，大幅减小推送大小。

## 推送步骤

### 步骤 1: 准备 GitHub Token

如果还没有 token：
1. 访问：https://github.com/settings/tokens/new
2. 填写信息：
   - Note: "StreamDiffusion Push"
   - 权限: 勾选 ✅ `repo`
3. 生成并复制 token

### 步骤 2: 推送代码

```bash
cd /root/StreamDiffusion
git push -u origin temp-main:main --force
```

提示输入时：
- **Username**: `Chee-0806`
- **Password**: 粘贴你的 token（不是 GitHub 密码）

### 步骤 3: 验证推送

推送成功后，访问仓库验证：
https://github.com/Chee-0806/StreamDiffusion

## 如果仍然遇到问题

### 方案 A: 在 URL 中嵌入 Token

```bash
# 替换 YOUR_TOKEN 为你的实际 token
git remote set-url origin https://YOUR_TOKEN@gh-proxy.com/https://github.com/Chee-0806/StreamDiffusion.git
git push -u origin temp-main:main --force

# 推送完成后，记得移除 token（安全考虑）
git remote set-url origin https://gh-proxy.com/https://github.com/Chee-0806/StreamDiffusion.git
```

### 方案 B: 使用 SSH（如果已配置）

```bash
git remote set-url origin git@github.com:Chee-0806/StreamDiffusion.git
git push -u origin temp-main:main --force
```

## 当前分支状态

- **当前分支**: `temp-main`
- **包含**: 所有最新代码（194 个文件）
- **历史**: 无历史记录（干净提交）
- **大小**: 大幅减小

## 注意事项

⚠️ **使用 `--force` 会覆盖远程 main 分支的历史**

如果远程仓库已有重要历史，建议：
1. 先备份远程仓库
2. 或者创建新分支推送：`git push -u origin temp-main:temp-main`

## 推送成功后

推送成功后，可以：
1. 切换到 main 分支并同步：
   ```bash
   git checkout -b main
   git push -u origin main
   ```

2. 或者直接在 GitHub 上合并 temp-main 到 main

