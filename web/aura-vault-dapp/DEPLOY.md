# 🚀 部署到 Vercel 指南

## 步骤 1: 本地构建测试
```bash
npm run build
npm run start
```

## 步骤 2: 部署到 Vercel

### 方法一：Vercel CLI
```bash
npm install -g vercel
vercel --prod
```

### 方法二：GitHub 集成
1. 推送代码到 GitHub
2. 登录 [vercel.com](https://vercel.com)
3. 导入 GitHub 仓库
4. 自动部署

### 方法三：直接上传
1. 打包项目: `npm run build`
2. 上传 `build/` 文件夹到 Vercel

## 环境变量配置
在 Vercel 控制台设置以下环境变量：
- `GENERATE_SOURCEMAP=false`
- `SKIP_PREFLIGHT_CHECK=true`

## 验证部署
部署完成后，访问你的 Vercel URL 测试：
- ✅ 钱包连接功能
- ✅ 合约读取功能
- ✅ 合约写入功能
- ✅ 移动端响应式布局

## 故障排除
- 如果构建失败，检查 `vercel.json` 配置
- 确保所有依赖已安装
- 检查环境变量设置