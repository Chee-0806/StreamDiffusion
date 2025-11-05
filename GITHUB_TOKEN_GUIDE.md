# GitHub Personal Access Token 创建指南

## 步骤 1: 登录 GitHub

访问 https://github.com 并登录你的账号（Chee-0806）

## 步骤 2: 进入 Token 设置页面

有两种方式：

### 方式 A: 直接访问
访问：https://github.com/settings/tokens

### 方式 B: 通过菜单
1. 点击右上角头像
2. 选择 **Settings**（设置）
3. 左侧菜单找到 **Developer settings**（开发者设置）
4. 点击 **Personal access tokens**（个人访问令牌）
5. 选择 **Tokens (classic)**（经典令牌）

## 步骤 3: 生成新 Token

1. 点击 **Generate new token**（生成新令牌）
2. 选择 **Generate new token (classic)**（生成经典令牌）
3. 如果提示输入密码，输入你的 GitHub 密码

## 步骤 4: 配置 Token

1. **Note**（备注）：输入一个描述，例如 "StreamDiffusion Push"
2. **Expiration**（过期时间）：选择过期时间（建议选择较长时间，如 90 天或 1 年）
3. **Select scopes**（选择权限）：**必须勾选 `repo`**
   - ✅ **repo** - 完整仓库访问权限（包括私有仓库）
   - 这将允许你推送代码

## 步骤 5: 生成并复制 Token

1. 滚动到页面底部
2. 点击 **Generate token**（生成令牌）按钮
3. **重要**：Token 只会显示一次，请立即复制保存！
   - 页面会显示类似 `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` 的字符串
   - 这就是你的 Personal Access Token

## 步骤 6: 使用 Token 推送代码

```bash
cd /root/StreamDiffusion
git push -u origin main
```

当提示时：
- **Username**: Chee-0806
- **Password**: 粘贴你的 token（不是 GitHub 密码！）

## 注意事项

⚠️ **安全提示**：
- Token 相当于密码，请妥善保管
- 不要将 token 提交到代码仓库
- 如果 token 泄露，立即在 GitHub 上删除它并生成新的

## 如果忘记 Token

如果忘记或丢失 token：
1. 访问 https://github.com/settings/tokens
2. 找到对应的 token（通过 Note 识别）
3. 点击删除，然后重新创建新的

## 快速链接

- Token 管理页面：https://github.com/settings/tokens
- 直接创建 Token：https://github.com/settings/tokens/new

