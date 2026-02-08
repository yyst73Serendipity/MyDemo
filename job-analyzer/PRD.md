# 岗位分析解读工具 - 产品需求文档（PRD）

## 1. 项目概述

### 1.1 项目背景
帮助求职者快速理解岗位要求，将复杂的职位描述转化为易理解的工作内容说明，并提供针对性的面试准备问题。

### 1.2 项目目标
- 自动化解析职位描述，提取关键信息
- 用通俗易懂的语言解读岗位要求
- 生成针对性的面试准备问题
- 以表格形式清晰展示分析结果

### 1.3 目标用户
- 求职者
- HR/招聘人员（用于优化JD）
- 职业规划师

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 文本输入功能
- **功能描述**：用户可以通过粘贴方式输入职位描述文本
- **输入方式**：
  - 支持大段文本粘贴
  - 文本框支持多行输入
  - 自动识别换行和分点格式
- **输入限制**：
  - 最大字符数：10000字符
  - 支持中英文混合
- **交互要求**：
  - 提供占位符提示："请粘贴职位描述..."
  - 支持清空按钮
  - 显示字符计数（可选）

#### 2.1.2 模型选择功能
- **功能描述**：用户可以在分析前选择使用的具体AI模型
- **支持的模型**（共9个）：
  - **OpenAI 系列**：GPT-5.1、GPT-4o
  - **Google Gemini 系列**：Gemini-2.5-Pro、Gemini-3-Pro-Preview
  - **DeepSeek 系列**：DeepSeek-R1、DeepSeek-V3
  - **Qwen 系列**：Qwen3-Max、Qwen3-Max-Preview
  - **Kimi 系列**：Kimi-K2
- **选择方式**：
  - 下拉选择框（Select）
  - 默认选择：第一个可用模型（通常为GPT-5.1）
  - 选择后立即生效，无需刷新页面
- **UI展示**：
  - 显示模型显示名称（如"GPT-5.1"）
  - 显示模型可用状态（可用/不可用）
  - 未配置API密钥时显示提示信息
- **交互要求**：
  - 选择器位于输入框上方
  - 清晰的视觉区分
  - 移动端友好的布局

#### 2.1.3 智能分析功能
- **功能描述**：调用用户选择的AI API对职位描述进行智能分析
- **分析维度**：
  1. **职位描述原文**：按原文分点拆解，保持原有格式和编号
  2. **大白话解读**：用通俗语言解释每一条的实际工作内容和能力要求
  3. **面试准备问题**：基于前两项分析，生成可能的面试问题
- **处理流程**：
  1. 用户选择模型（如未选择，使用默认模型）
  2. 用户点击"开始分析"按钮
  3. 显示加载状态（Loading），显示当前使用的API名称
  4. 调用选定的AI API（带重试机制）
  5. 解析返回的 JSON/结构化数据
  6. 渲染到表格中
- **错误处理**：
  - API调用失败：显示错误提示，提示当前使用的API，允许重试或切换API
  - 解析失败：提示用户重新分析或尝试其他API
  - 网络超时：30秒超时，提示用户检查网络或切换API
  - API密钥未配置：提示用户配置对应API的密钥

#### 2.1.4 结果展示功能
- **展示格式**：三列表格
  - 列1：职位描述原文
  - 列2：大白话解读
  - 列3：面试准备哪些问题
- **表格特性**：
  - 响应式设计，适配不同屏幕
  - 支持列宽调整
  - 单元格内容支持换行
  - 支持文本复制
- **样式要求**：
  - 清晰的表头
  - 交替行背景色（斑马纹）
  - 合适的字体大小和行高
  - 移动端友好

#### 2.1.5 复制表格功能
- **功能描述**：将分析结果表格复制到剪贴板
- **支持格式**：
  - HTML格式：适合粘贴到Word、Excel、邮件等应用，保留表格结构和样式
  - Markdown格式：适合文档、笔记应用，使用Markdown表格语法
  - 纯文本格式：制表符分隔，适合粘贴到Excel等应用
- **复制方式**：
  - 点击"复制表格"按钮
  - 从下拉菜单选择格式（HTML/Markdown/纯文本）
  - 自动复制到剪贴板
  - 显示复制成功提示
- **技术实现**：
  - 使用 `navigator.clipboard.writeText()` API
  - 包含降级方案（使用 `document.execCommand('copy')`）
  - 处理HTML内容转换（questions字段可能包含HTML）

### 2.2 辅助功能

#### 2.2.1 加载状态
- 分析过程中显示加载动画
- 显示进度提示："正在分析中，请稍候..."
- 禁用分析按钮，防止重复提交

#### 2.2.2 错误提示
- API调用失败
- 网络错误
- 输入为空
- 友好的错误提示文案

## 3. 非功能需求

### 3.1 性能要求
- 页面加载时间 < 2秒
- API响应时间 < 30秒（取决于Gemini API）
- 复制操作响应时间 < 1秒

### 3.2 兼容性要求
- 浏览器：Chrome、Edge、Firefox、Safari（最新版本）
- 移动端：iOS Safari、Chrome Mobile
- 响应式设计，支持平板和手机

### 3.3 安全性要求
- API密钥存储在环境变量中（前端环境变量）
  - 统一使用 DMXAPI 平台的一个 API KEY
  - 所有模型共享同一个 API KEY，无需单独配置
- 不在代码中硬编码密钥
- 使用 HTTPS 传输
- 密钥验证：调用前检查对应API密钥是否配置

### 3.4 可用性要求
- 界面简洁直观
- 操作流程不超过3步
- 提供清晰的操作反馈

## 4. 页面设计

### 4.1 页面结构

```
┌─────────────────────────────────────┐
│         页面标题/Logo                │
│      "岗位分析解读工具"              │
├─────────────────────────────────────┤
│                                     │
│  【输入区域】                        │
│                                     │
│  模型选择：[下拉选择框：GPT-5.1 ▼]     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │   职位描述输入框（多行）      │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [清空]  [开始分析]                  │
│                                     │
├─────────────────────────────────────┤
│                                     │
│  【结果展示区域】                    │
│  ┌─────────────────────────────┐   │
│  │ 职位描述原文 │ 大白话解读 │ 面试问题 │
│  ├─────────────────────────────┤   │
│  │  1. ...     │  ...        │  ...   │
│  │  2. ...     │  ...        │  ...   │
│  └─────────────────────────────┘   │
│                                     │
│  [复制表格 ▼]                        │
│                                     │
└─────────────────────────────────────┘
```

### 4.2 页面布局

#### 4.2.1 桌面端布局
- 最大宽度：1200px，居中显示
- 输入区域：占页面宽度的80%
- 表格区域：全宽，支持横向滚动（如需要）

#### 4.2.2 移动端布局
- 全宽显示
- 模型选择器：下拉选择框，显示所有可用模型
- 输入框和按钮堆叠显示
- 表格支持横向滚动
- 字体大小适配移动端

#### 4.2.3 模型选择器布局
- **桌面端**：
  - 水平排列，单行显示
  - 使用Radio Group组件
  - 每个选项显示API名称和图标（可选）
- **移动端**：
  - 可横向滚动或垂直堆叠
  - 触摸友好的按钮大小
  - 清晰的选中状态

### 4.3 视觉设计

#### 4.3.1 配色方案
- 主色调：蓝色系（专业、可信）
- 辅助色：灰色（文本、边框）
- 强调色：绿色（成功状态）
- 警告色：红色（错误提示）

#### 4.3.2 字体
- 标题：18-24px，加粗
- 正文：14-16px
- 表格内容：14px
- 按钮文字：14-16px

#### 4.3.3 间距
- 页面边距：16-24px
- 元素间距：12-16px
- 表格内边距：12px

## 5. 技术架构

### 5.1 技术栈选型

#### 5.1.1 前端框架
- **React 18+** + **TypeScript**
  - 理由：生态成熟，组件化开发，类型安全

#### 5.1.2 构建工具
- **Vite**
  - 理由：快速构建，开发体验好，支持TypeScript

#### 5.1.3 UI组件库
- **Ant Design (antd)**
  - 理由：表格组件强大，样式美观，文档完善
  - 或 **shadcn/ui** + **Tailwind CSS**（更轻量）

#### 5.1.4 样式方案
- **CSS Modules** 或 **Tailwind CSS**
  - 理由：样式隔离，易于维护

#### 5.1.5 AI API调用
- **多API支持**：
  - **@google/generative-ai** (Gemini SDK) - Google官方SDK
  - **openai** (OpenAI SDK) - OpenAI官方SDK
  - **axios** 或 **fetch** (DeepSeek API) - RESTful API调用
  - 理由：支持用户选择不同AI模型，提供灵活性

#### 5.1.6 复制功能
- **Clipboard API (navigator.clipboard.writeText)**
  - 理由：现代浏览器标准API，支持文本复制
  - 降级方案：使用 `document.execCommand('copy')` 兼容旧浏览器

#### 5.1.7 状态管理
- **React Hooks (useState, useEffect)**
  - 理由：简单场景，无需复杂状态管理

### 5.2 项目结构

```
job-analyzer/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── InputArea.tsx          # 输入区域组件
│   │   ├── ModelSelector.tsx      # 模型选择器组件
│   │   ├── ResultTable.tsx        # 结果表格组件
│   │   ├── LoadingSpinner.tsx     # 加载动画
│   │   └── ErrorMessage.tsx       # 错误提示
│   ├── services/
│   │   └── apiService.ts           # API服务统一接口（通过DMXAPI接入所有模型）
│   ├── types/
│   │   └── index.ts               # TypeScript类型定义
│   ├── utils/
│   │   ├── copyTable.ts           # 表格复制工具
│   │   ├── promptBuilder.ts       # Prompt构建工具
│   │   └── parseResponse.ts       # 解析API响应
│   ├── App.tsx                     # 主组件
│   ├── index.tsx                   # 入口文件
│   └── styles/
│       └── index.css               # 全局样式
├── .env.local                      # 环境变量（DMXAPI统一配置）
│                                    # VITE_DMXAPI_API_KEY
│                                    # VITE_DMXAPI_BASE_URL（可选）
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 5.3 API设计

#### 5.3.1 统一API接口设计

**API类型定义**：
```typescript
type ApiProvider = 'gemini' | 'openai' | 'deepseek';

interface ApiConfig {
  provider: ApiProvider;
  apiKey: string;
  model?: string;  // 可选，不同API的模型名称
}
```

**统一调用接口**：
```typescript
interface AnalyzeRequest {
  text: string;           // 职位描述文本
  provider: ApiProvider;  // 选择的API
  apiKey: string;         // API密钥
}

interface AnalyzeResponse {
  items: AnalysisItem[];
  provider: ApiProvider;  // 使用的API
}
```

#### 5.3.2 API调用方式（统一通过DMXAPI）

本项目使用 **DMXAPI 聚合平台**统一接入所有AI模型，所有模型都使用 OpenAI SDK 兼容格式调用。

**统一配置**：
```env
VITE_DMXAPI_API_KEY=your_dmxapi_api_key
VITE_DMXAPI_BASE_URL=https://www.dmxapi.com/v1
```

**统一调用方式**：
```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: dmxApiKey,      // DMXAPI API KEY
  baseURL: dmxBaseUrl,    // DMXAPI Base URL
  dangerouslyAllowBrowser: true
});

// 所有模型统一使用相同的调用方式
const completion = await client.chat.completions.create({
  model: modelId,         // DMXAPI 中的模型 ID（gemini-pro / gpt-4 / deepseek-chat）
  messages: [
    { role: "system", content: "系统提示" },
    { role: "user", content: "用户prompt" }
  ],
  temperature: 0.7,
  max_tokens: 4000
});
```

**模型 ID 映射**：
- Gemini → `gemini-pro`（DMXAPI 中的模型 ID）
- GPT → `gpt-4`（DMXAPI 中的模型 ID）
- DeepSeek → `deepseek-chat`（DMXAPI 中的模型 ID）

**Prompt设计**：
```
你是一个专业的职位分析助手。请分析以下职位描述，并按照以下格式输出JSON：

{
  "items": [
    {
      "original": "职位描述原文（保持原格式）",
      "interpretation": "大白话解读",
      "questions": "面试准备问题（用<br>分隔多个问题）"
    }
  ]
}

职位描述：
{用户输入的职位描述}

要求：
1. 职位描述原文要按照原文的分点来拆解，保持原有编号和格式
2. 大白话解读要说明这个岗位实际可能做什么工作、需要什么能力
3. 面试准备问题要结合前两项分析，思考面试官可能会问什么问题，每个问题用<br>分隔
4. 输出必须是有效的JSON格式，不要包含markdown代码块标记
```

**响应格式**：
```typescript
interface AnalysisItem {
  original: string;      // 职位描述原文
  interpretation: string; // 大白话解读
  questions: string;      // 面试问题（HTML格式，包含<br>）
}

interface AnalysisResult {
  items: AnalysisItem[];
}
```

### 5.4 核心流程

```
用户选择模型（默认第一个可用模型）
    ↓
用户输入职位描述
    ↓
点击"开始分析"
    ↓
显示Loading状态（显示当前使用的模型）
    ↓
根据选择的模型构建请求（通过DMXAPI）
    ↓
构建Prompt
    ↓
调用选定的AI API
    ↓
解析JSON响应（统一格式）
    ↓
渲染表格
    ↓
显示结果（显示使用的模型信息）
    ↓
（可选）复制表格
```

## 6. 开发计划

### 6.1 开发阶段

#### Phase 1: 项目初始化（1天）
- [ ] 搭建React + TypeScript + Vite项目
- [ ] 配置Ant Design
- [ ] 配置环境变量
- [ ] 基础页面布局

#### Phase 2: 核心功能开发（3-4天）
- [ ] 输入区域组件开发
- [ ] 模型选择器组件开发
- [ ] DMXAPI统一服务层开发
  - [ ] DMXAPI配置和初始化
  - [ ] 模型配置管理（9个模型）
  - [ ] 统一API调用接口
- [ ] Prompt设计和优化（适配不同API）
- [ ] 响应解析逻辑（统一格式处理）
- [ ] 表格展示组件

#### Phase 3: 复制功能（1天）
- [ ] 复制表格功能实现（HTML/Markdown/纯文本）
- [ ] 格式转换逻辑优化
- [ ] Clipboard API集成和降级方案

#### Phase 4: 优化和测试（1-2天）
- [ ] 错误处理完善
- [ ] 加载状态优化
- [ ] 响应式设计优化
- [ ] 浏览器兼容性测试
- [ ] 性能优化

#### Phase 5: 部署（0.5天）
- [ ] 构建生产版本
- [ ] 部署到Vercel/Netlify
- [ ] 配置环境变量

**总计：6-8天**（因增加多API支持功能，开发时间略有增加）

### 6.2 技术难点和解决方案

#### 难点1：Gemini API返回格式不稳定
- **解决方案**：
  - 设计清晰的Prompt，明确要求JSON格式
  - 添加JSON解析错误处理
  - 如果解析失败，尝试提取JSON部分
  - 提供重试机制

#### 难点2：不同格式的表格数据转换
- **解决方案**：
  - HTML格式：保留questions字段的HTML结构，转义其他字段的特殊字符
  - Markdown格式：将HTML转换为纯文本，转义Markdown特殊字符
  - 纯文本格式：移除所有HTML标签，使用制表符分隔
  - 处理换行符和特殊字符的转义
  - 测试不同格式在不同应用中的粘贴效果

#### 难点3：长文本处理
- **解决方案**：
  - 设置合理的token限制
  - 如果文本过长，提示用户分段输入
  - 优化Prompt，减少不必要的输出

#### 难点4：多API适配和统一接口
- **解决方案**：
  - 设计统一的API接口抽象层
  - 不同API的请求格式统一封装
  - 不同API的响应格式统一解析
  - 错误处理统一化，但保留API特定的错误信息
  - 使用策略模式或工厂模式管理不同API服务

## 7. 后续优化方向（可选）

1. **图片输入支持**：集成OCR功能
2. **历史记录**：本地存储分析历史
3. **批量分析**：支持多个职位描述批量处理
4. **模板功能**：保存常用职位类型模板
5. **分享功能**：生成分享链接
6. **多语言支持**：支持英文职位描述分析

## 8. 风险评估

### 8.1 技术风险
- **多API稳定性**：中等风险
  - 缓解：添加重试机制，错误提示，支持切换API
  - 不同API的可用性和响应速度可能不同
- **API调用成本**：低风险（用户确认无预算限制）
  - 不同API的定价策略不同，用户可自行选择
- **API密钥管理**：中等风险
  - 缓解：环境变量管理，密钥验证，友好的错误提示
- **浏览器兼容性**：低风险
  - 缓解：使用成熟库，充分测试

### 8.2 产品风险
- **AI分析质量不稳定**：中等风险
  - 缓解：优化Prompt，添加示例，允许用户重新分析
- **用户输入格式不规范**：低风险
  - 缓解：提供输入示例，智能识别格式

## 9. API配置说明

### 9.1 支持的API列表

本项目使用 **DMXAPI 聚合平台**统一接入多个AI模型，所有模型共享同一个 API KEY。

| API提供商 | 模型名称 | SDK/库 | 接入方式 |
|---------|---------|--------|----------|
| Google Gemini | gemini-pro | openai (兼容格式) | 通过 DMXAPI |
| OpenAI | gpt-4 | openai | 通过 DMXAPI |
| DeepSeek | deepseek-chat | openai (兼容格式) | 通过 DMXAPI |

### 9.2 API密钥配置

**开发环境**（.env.local）：
```env
# DMXAPI 聚合平台配置（统一配置）
VITE_DMXAPI_API_KEY=your_dmxapi_api_key_here
VITE_DMXAPI_BASE_URL=https://www.dmxapi.com/v1
```

**生产环境**：
- Vercel/Netlify：在平台的环境变量设置中配置 `VITE_DMXAPI_API_KEY` 和 `VITE_DMXAPI_BASE_URL`
- 只需配置一个 DMXAPI API KEY 即可使用所有模型

**获取 API KEY**：
1. 访问 [DMXAPI 控制台](https://dmxapi.cn)
2. 注册账号并登录
3. 在控制台生成 API KEY
4. 将 API KEY 配置到环境变量中

### 9.3 模型选择逻辑

1. **默认选择**：第一个可用模型（通常为GPT-5.1，如果 DMXAPI 已配置）
2. **可用性检查**：检查 DMXAPI API KEY 是否配置
3. **用户选择**：用户可随时切换不同的模型（从9个模型中选择）
4. **错误处理**：如果 DMXAPI API KEY 未配置，提示用户配置，并禁用所有模型

### 9.4 Prompt适配

所有模型通过DMXAPI统一接入，使用OpenAI SDK兼容格式：
- **统一格式**：使用messages数组格式（system + user）
- **统一接口**：所有模型使用相同的API调用方式
- **核心Prompt内容保持一致**，确保输出格式统一

---

## 附录：示例Prompt（最终版）

```
你是一个专业的职位分析助手。请分析以下职位描述，并按照以下格式输出JSON：

{
  "items": [
    {
      "original": "职位描述原文的第一条（保持原格式，包括编号）",
      "interpretation": "用大白话解释这条要求实际是做什么工作、需要什么能力",
      "questions": "问题1<br>问题2<br>问题3"
    },
    {
      "original": "职位描述原文的第二条",
      "interpretation": "大白话解读",
      "questions": "问题1<br>问题2"
    }
  ]
}

职位描述：
{用户输入的职位描述}

重要要求：
1. 职位描述原文（original字段）必须严格按照原文的分点来拆解，保持原有的编号、格式和措辞
2. 大白话解读（interpretation字段）要说明这个岗位实际可能做什么工作、需要什么能力，用通俗易懂的语言
3. 面试准备问题（questions字段）要结合前两项分析，思考面试官可能会问什么问题，每个问题用<br>分隔，问题要有针对性和实用性
4. 输出必须是有效的JSON格式，不要包含markdown代码块标记（如```json）
5. 如果职位描述中有多条要求，请拆解成多个items
```

---

**文档版本**：v1.1  
**创建日期**：2024  
**最后更新**：2024  
**更新内容**：v1.2 - 统一使用DMXAPI接入，支持9个具体模型选择；将图片导出功能替换为复制表格功能（支持HTML/Markdown/纯文本三种格式）
