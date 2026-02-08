# 快速开始指南

## 1. 安装依赖

```bash
npm install
```

## 2. 配置API密钥

创建 `.env.local` 文件（参考 `.env.example`），配置 DMXAPI 密钥：

```env
# DMXAPI 聚合平台配置（统一配置）
VITE_DMXAPI_API_KEY=your_dmxapi_api_key_here
VITE_DMXAPI_BASE_URL=https://www.dmxapi.com/v1
```

**说明**：
- 所有9个模型统一使用 DMXAPI 平台的一个 API KEY
- 请在 [DMXAPI 控制台](https://dmxapi.cn) 生成并填写 API KEY
- `VITE_DMXAPI_BASE_URL` 为可选配置，默认值为 `https://www.dmxapi.com/v1`

## 3. 启动开发服务器

```bash
npm run dev
```

浏览器会自动打开 `http://localhost:3000`

## 4. 使用步骤

1. **选择模型**：在输入框上方选择要使用的AI模型（从9个模型中选择）
2. **输入职位描述**：粘贴或输入职位描述文本
3. **点击分析**：点击"开始分析"按钮
4. **查看结果**：等待分析完成，查看表格结果
5. **复制表格**：点击"复制表格"按钮，选择格式（HTML/Markdown/纯文本）后复制到剪贴板

## 常见问题

### Q: 提示"未配置API密钥"？
A: 请检查 `.env.local` 文件是否存在，且 `VITE_DMXAPI_API_KEY` 配置正确。注意变量名必须以 `VITE_` 开头。

### Q: API调用失败？
A: 
- 检查 DMXAPI API 密钥是否有效
- 检查网络连接
- 确认 DMXAPI 账户余额充足
- 尝试切换其他模型
- 查看浏览器控制台的错误信息

### Q: 如何获取API密钥？
A: 访问 [DMXAPI 控制台](https://dmxapi.cn) 注册账号并生成 API KEY，参考 README.md 中的"API密钥获取"章节。

### Q: 复制表格失败？
A: 
- 确保浏览器支持 Clipboard API（现代浏览器均支持）
- 检查浏览器权限设置，确保允许访问剪贴板
- 如果复制失败，系统会自动使用降级方案
- 尝试使用其他浏览器

## 开发命令

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```
