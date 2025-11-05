# Git 推送修复指南

## 问题：HTTP 413 错误

推送时遇到 `error: RPC failed; HTTP 413` 表示推送的数据太大。

## 已完成的修复

1. ✅ **更新 .gitignore**：排除 TensorRT engine 文件
   - `*.engine`
   - `*.engine.onnx`
   - `*.engine.opt.onnx`
   - `engines/` 目录

2. ✅ **增加 HTTP 缓冲区**：
   ```bash
   git config http.postBuffer 1048576000  # 1GB
   ```

3. ✅ **临时禁用压缩**（用于大文件推送）：
   ```bash
   git config core.compression 0
   ```

## 推送方式

### 方式 1: 使用 Personal Access Token（推荐）

```bash
cd /root/StreamDiffusion
git push -u origin main
```

提示输入时：
- **Username**: `Chee-0806`
- **Password**: 粘贴你的 GitHub Personal Access Token

### 方式 2: 在 URL 中嵌入 Token（临时）

如果方式 1 不行，可以临时在 URL 中嵌入 token：

```bash
# 替换 YOUR_TOKEN 为你的实际 token
git remote set-url origin https://YOUR_TOKEN@gh-proxy.com/https://github.com/Chee-0806/StreamDiffusion.git
git push -u origin main

# 推送完成后，记得移除 token（安全考虑）
git remote set-url origin https://gh-proxy.com/https://github.com/Chee-0806/StreamDiffusion.git
```

### 方式 3: 分批推送

如果推送仍然失败，可以尝试分批推送：

```bash
# 只推送最近的提交
git push -u origin HEAD~5:main  # 推送最近 5 个提交
```

或者使用 `--force-with-lease`（谨慎使用）：

```bash
git push -u origin main --force-with-lease
```

## 创建 GitHub Token

如果还没有 token：

1. 访问：https://github.com/settings/tokens/new
2. 填写信息：
   - Note: "StreamDiffusion Push"
   - Expiration: 选择过期时间
   - 权限: 勾选 ✅ `repo`
3. 点击 "Generate token"
4. 立即复制 token（只显示一次）

## 验证推送

推送成功后，可以访问仓库验证：
https://github.com/Chee-0806/StreamDiffusion

## 如果仍然失败

如果仍然遇到 HTTP 413 错误：

1. **检查大文件**：
   ```bash
   git ls-files | xargs -I {} du -h {} | sort -rh | head -20
   ```

2. **使用 Git LFS**（如果需要推送大文件）：
   ```bash
   git lfs install
   git lfs track "*.engine"
   git add .gitattributes
   git commit -m "Add Git LFS tracking"
   ```

3. **考虑移除不必要的大文件**：
   - 检查是否有不需要的 GIF、视频等大文件
   - 这些文件可以通过 `.gitignore` 排除

