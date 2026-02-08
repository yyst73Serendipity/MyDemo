# 岗位分析解读工具

一个智能化的职位描述分析工具，帮助求职者快速理解岗位要求，将复杂的职位描述转化为易理解的工作内容说明，并提供针对性的面试准备问题。

## 功能特性

- 🤖 **多AI模型支持**：支持9个具体模型，包括GPT-5.1、GPT-4o、Gemini-2.5-Pro、Gemini-3-Pro-Preview、DeepSeek-R1、DeepSeek-V3、Qwen3-Max、Qwen3-Max-Preview、Kimi-K2
- 📝 **智能分析**：自动拆解职位描述，生成大白话解读和面试问题
- 📊 **表格展示**：清晰的三列表格展示分析结果
- 📋 **复制表格**：支持将分析结果复制为HTML、Markdown或纯文本格式
- 🎨 **响应式设计**：适配桌面端和移动端

## 技术栈

- **前端框架**：React 18 + TypeScript
- **构建工具**：Vite
- **UI组件库**：Ant Design 5
- **AI SDK**：openai (统一使用 OpenAI SDK 兼容格式，通过 DMXAPI 聚合平台接入)

## 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 7.0.0

### 安装依赖

```bash
npm install
```

### 配置API密钥

1. 复制 `.env.example` 文件为 `.env.local`
2. 填入你的 DMXAPI 密钥：

```env
# DMXAPI 聚合平台配置（统一配置）
VITE_DMXAPI_API_KEY=your_dmxapi_api_key_here
VITE_DMXAPI_BASE_URL=https://www.dmxapi.com/v1
```

**注意**：
- 所有模型统一使用 DMXAPI 平台的一个 API KEY
- 请在 [DMXAPI 控制台](https://dmxapi.cn) 生成并填写 API KEY
- `VITE_DMXAPI_BASE_URL` 为可选配置，默认值为 `https://www.dmxapi.com/v1`

### 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

## 使用说明

1. **选择模型**：在输入区域上方选择要使用的AI模型（从9个模型中选择）
2. **输入职位描述**：在文本框中粘贴或输入职位描述文本
3. **开始分析**：点击"开始分析"按钮
4. **查看结果**：分析完成后，结果将以表格形式展示
5. **复制表格**：点击"复制表格"按钮，选择格式（HTML/Markdown/纯文本）后复制到剪贴板

## 项目结构

```
job-analyzer/
├── public/              # 静态资源
├── src/
│   ├── components/     # React组件
│   │   ├── ModelSelector.tsx    # 模型选择器
│   │   ├── InputArea.tsx        # 输入区域
│   │   ├── ResultTable.tsx      # 结果表格
│   │   ├── LoadingSpinner.tsx   # 加载动画
│   │   └── ErrorMessage.tsx     # 错误提示
│   ├── services/       # API服务层
│   │   └── apiService.ts        # 统一API接口（通过DMXAPI接入所有模型）
│   ├── types/          # TypeScript类型定义
│   │   └── index.ts
│   ├── utils/          # 工具函数
│   │   ├── promptBuilder.ts     # Prompt构建
│   │   ├── parseResponse.ts     # 响应解析
│   │   └── copyTable.ts          # 表格复制
│   ├── styles/         # 样式文件
│   │   └── index.css
│   ├── App.tsx         # 主应用组件
│   └── main.tsx        # 应用入口
├── .env.example        # 环境变量示例
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## API密钥获取

本项目使用 **DMXAPI 聚合平台**统一接入多个AI模型，只需配置一个 API KEY 即可使用所有模型。

### DMXAPI 配置步骤

1. 访问 [DMXAPI 控制台](https://dmxapi.cn)
2. 注册账号并登录
3. 在控制台生成 API KEY
4. 将 API KEY 配置到 `.env.local` 文件中的 `VITE_DMXAPI_API_KEY`

### 支持的模型

通过 DMXAPI 平台，你可以使用以下9个模型：

**OpenAI 系列**：
- GPT-5.1
- GPT-4o

**Google Gemini 系列**：
- Gemini-2.5-Pro
- Gemini-3-Pro-Preview

**DeepSeek 系列**：
- DeepSeek-R1
- DeepSeek-V3

**Qwen 系列**：
- Qwen3-Max
- Qwen3-Max-Preview

**Kimi 系列**：
- Kimi-K2

所有模型共享同一个 DMXAPI API KEY，无需单独配置各个厂商的密钥。

## 注意事项

- ⚠️ **API密钥安全**：请勿将 `.env.local` 文件提交到Git仓库
- ⚠️ **API调用成本**：使用AI API可能产生费用，请注意控制使用量
- ⚠️ **浏览器限制**：通过DMXAPI统一接入，无需在浏览器中直接调用各厂商SDK

## 开发计划

- [x] 项目初始化
- [x] 多API支持
- [x] 核心功能开发
- [x] 复制表格功能
- [ ] 图片输入支持（OCR）
- [ ] 历史记录功能
- [ ] 批量分析功能

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue。
