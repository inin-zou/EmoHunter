# 🚀 部署到 Vercel 指南

## 步骤 1: 本地构建测试
```bash
npm run build
npm run start
```

## 步骤 2: 部署静态构建产物

### 方法1：本地构建后直接部署
```bash
npm run build
vercel --prod --cwd build
```

### 方法2：Vercel Dashboard 手动上传
1. 运行 `npm run build` 生成本地 build
2. 访问 [vercel.com](https://vercel.com)
3. 点击 "New Project" → "Upload"
4. 拖拽整个 `build/` 文件夹上传
5. 自动部署

### 方法3：Vercel CLI 部署静态目录
```bash
npm run build
vercel build --prod
vercel deploy --prebuilt
```

### 方法4：GitHub Actions 自动部署
创建 `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-args: '--prod'
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

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