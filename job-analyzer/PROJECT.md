# 项目文档

## 项目概述

**项目名称**：岗位分析解读工具  
**项目类型**：Web前端应用  
**技术栈**：React + TypeScript + Vite + Ant Design  
**开发状态**：开发中

## 项目目标

帮助求职者快速理解岗位要求，将复杂的职位描述转化为易理解的工作内容说明，并提供针对性的面试准备问题。

## 核心功能

### 1. 模型选择功能
- 支持选择9个具体AI模型（GPT-5.1、GPT-4o、Gemini-2.5-Pro、Gemini-3-Pro-Preview、DeepSeek-R1、DeepSeek-V3、Qwen3-Max、Qwen3-Max-Preview、Kimi-K2）
- 通过DMXAPI统一接入，只需配置一个API KEY
- 下拉选择模式，切换即时生效

### 2. 文本输入功能
- 支持大段文本粘贴
- 多行文本输入框
- 字符计数显示
- 最大字符数限制：10000

### 3. 智能分析功能
- 调用选定的AI API进行分析
- 自动拆解职位描述原文
- 生成大白话解读
- 生成面试准备问题

### 4. 结果展示功能
- 三列表格展示：
  - 职位描述原文
  - 大白话解读
  - 面试准备哪些问题
- 响应式设计
- 支持文本复制

### 5. 复制表格功能
- 支持HTML格式（适合粘贴到Word、Excel、邮件等）
- 支持Markdown格式（适合文档、笔记应用）
- 支持纯文本格式（制表符分隔，适合Excel）
- 一键复制到剪贴板

## 技术架构

### 前端架构
- **框架**：React 18（函数式组件 + Hooks）
- **语言**：TypeScript
- **构建工具**：Vite
- **UI库**：Ant Design 5
- **状态管理**：React Hooks（useState）

### API集成
- **Gemini**：@google/generative-ai SDK
- **OpenAI**：openai SDK
- **DeepSeek**：RESTful API（axios）

### 项目结构
```
src/
├── components/     # UI组件（展示层）
├── services/       # API服务（业务逻辑层）
├── utils/         # 工具函数（工具层）
├── types/         # 类型定义（类型层）
└── styles/         # 样式文件（样式层）
```

## 数据流

```
用户输入
  ↓
选择API
  ↓
点击分析
  ↓
构建Prompt
  ↓
调用AI API
  ↓
解析响应
  ↓
渲染表格
  ↓
（可选）复制表格
```

## 环境变量配置

| 变量名 | 说明 | 必需 |
|--------|------|------|
| VITE_DMXAPI_API_KEY | DMXAPI 聚合平台 API密钥 | 是（所有模型统一使用） |
| VITE_DMXAPI_BASE_URL | DMXAPI 基础URL | 否（默认：https://www.dmxapi.com/v1） |

**说明**：
- 所有9个模型统一使用 DMXAPI 平台的一个 API KEY
- 请在 [DMXAPI 控制台](https://dmxapi.cn) 生成并填写 API KEY

## 开发规范

### 代码规范
- 使用TypeScript严格模式
- 遵循ESLint规则
- 文件命名采用驼峰命名法（PascalCase用于组件，camelCase用于函数/变量）
- 代码中保留适当的中文注释

### 文件命名规范
- 组件文件：PascalCase，如 `ApiSelector.tsx`
- 工具文件：camelCase，如 `promptBuilder.ts`
- 类型文件：`index.ts`
- 样式文件：`index.css`

### Git提交规范
- 每次修改后更新 `operateLog.md`
- 同步更新相关文档（README.md、PROJECT.md等）

## 已知问题

1. OpenAI SDK在浏览器中直接调用需要设置 `dangerouslyAllowBrowser: true`，生产环境建议使用后端代理
2. 不同API的响应格式可能略有差异，需要统一解析处理

## 后续优化方向

1. **图片输入支持**：集成OCR功能，支持图片上传
2. **历史记录**：本地存储分析历史
3. **批量分析**：支持多个职位描述批量处理
4. **模板功能**：保存常用职位类型模板
5. **分享功能**：生成分享链接
6. **多语言支持**：支持英文职位描述分析

## 开发计划

### Phase 1: 项目初始化 ✅
- [x] 搭建React + TypeScript + Vite项目
- [x] 配置Ant Design
- [x] 配置环境变量
- [x] 基础页面布局

### Phase 2: 核心功能开发 ✅
- [x] 输入区域组件开发
- [x] API选择器组件开发
- [x] 多API服务层开发
- [x] Prompt设计和优化
- [x] 响应解析逻辑
- [x] 表格展示组件

### Phase 3: 复制功能 ✅
- [x] 复制表格功能实现（HTML/Markdown/纯文本）
- [x] Clipboard API集成和降级方案
- [x] 格式转换逻辑实现

### Phase 4: 优化和测试 🚧
- [ ] 错误处理完善
- [ ] 加载状态优化
- [ ] 响应式设计优化
- [ ] 浏览器兼容性测试
- [ ] 性能优化

### Phase 5: 部署 ⏳
- [ ] 构建生产版本
- [ ] 部署到Vercel/Netlify
- [ ] 配置环境变量

## 参考资料

- [React官方文档](https://react.dev/)
- [TypeScript官方文档](https://www.typescriptlang.org/)
- [Vite官方文档](https://vitejs.dev/)
- [Ant Design官方文档](https://ant.design/)
- [Gemini API文档](https://ai.google.dev/docs)
- [OpenAI API文档](https://platform.openai.com/docs)
- [DeepSeek API文档](https://platform.deepseek.com/docs)
