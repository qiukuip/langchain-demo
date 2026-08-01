# LangChain Demo

LangChain/LangGraph 学习示例仓库，覆盖从基础 Agent 创建到多 Agent 协作、MCP 协议集成、中间件系统等核心主题。

## 项目结构

```
.
├── 00_overview/                  # 快速入门：创建第一个 Agent
├── 01-part-agents/               # Agent 创建与配置（17 个示例）
├── 02-part-models/               # 模型初始化与高级特性（22 个示例）
├── 03-part-messages/             # 消息类型与多模态内容（7 个示例）
├── 04-part-tools/                # 工具定义与运行时（10 个示例）
├── 05-part-short-term-memory/    # 对话记忆管理（8 个示例）
├── 06-part-event-stream/         # 事件流（2 个示例）
├── 07-part-streaming/            # 流式输出模式（10 个示例）
├── 08-structured-output/         # 结构化输出（3 个示例）
├── 09-part-middleware/           # 中间件深度解析（11 个示例）
├── 10_guardrails/                # 安全护栏（1 个示例）
├── 11_mcp/                       # MCP 协议（Model Context Protocol）
│   └── servers/                  #   MCP 服务端示例
├── 12_human_in_the_loop/         # 人机协作（1 个示例）
├── 13_multi_agent/               # 多 Agent 架构
│   ├── 01_sub_agents/            #   子 Agent 模式
│   ├── 02_handoffs/              #   Agent 交接模式
│   ├── 03_skills/                #   技能系统
│   └── 04_router/                #   路由分发模式
└── 14_long_term_memory/          # 长期记忆与存储（2 个示例）
```

## 环境要求

- Python 3.10+
- Google Gemini API Key

## 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:qiukuip/langchain-demo.git
cd langchain-demo

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install langchain langchain-google-genai langgraph python-dotenv pydantic langsmith
pip install langgraph-checkpoint-postgres  # PostgreSQL 持久化（可选）
pip install langchain-mcp-adapters mcp      # MCP 协议（可选）
pip install deepagents                       # DeepAgent 中间件（可选）

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

## 环境变量

在 `.env` 文件中配置以下变量：

```env
GOOGLE_API_KEY=your-google-api-key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=langchain-demo
SUPABASE_POSTGRES_PASSWORD=your-pg-password    # 可选，PostgreSQL 持久化时需要
```

## 各模块概览

### 00_overview - 快速入门
使用 `create_agent` 一行代码创建带工具的 Agent。

### 01-part-agents - Agent 创建与配置
从基础 Agent 构建到高级特性：动态模型选择、结构化输出、系统提示词、状态管理、上下文注入、流式输出、中间件配置、动态工具过滤等。

### 02-part-models - 模型初始化与特性
模型初始化方式、批量调用、工具绑定、可配置模型、速率限制、服务端工具调用（Google Search）、流式输出、结构化输出、Token 用量追踪等。

### 03-part-messages - 消息类型
SystemMessage/HumanMessage/AIMessage/ToolMessage 的使用，多模态消息，Tool Call 的完整生命周期。

### 04-part-tools - 工具定义
高级 Schema 定义、状态访问与更新、上下文访问、长期记忆存储、流式写入、错误处理。

### 05-part-short-term-memory - 短期记忆
对话记忆管理：消息裁剪、删除旧消息、自动摘要、基于 PostgreSQL 的持久化存储。

### 06-part-event-stream - 事件流
`stream_events()` API 的用法，子 Agent 事件流。

### 07-part-streaming - 流式输出
多种流式模式（updates/messages/custom）、思考过程流式、工具调用流式、安全护栏流式、人机协作流式、子 Agent 流式。

### 08-structured-output - 结构化输出
ProviderStrategy 和 ToolStrategy 两种策略，支持 BaseModel/dataclass/TypedDict/JSON Schema。

### 09-part-middleware - 中间件系统
Node-style hooks（before_model/after_model）、Wrap-style hooks（wrap_model_call/wrap_tool_call）、类式中间件、Agent 跳转控制等。

### 10_guardrails - 安全护栏
关键词拦截与 LLM 安全评估两种护栏模式。

### 11_mcp - MCP 协议
多服务器 MCP 客户端、有状态会话、结构化内容、Prompt 和 Resource 加载、拦截器链、用户信息获取。

### 12_human_in_the_loop - 人机协作
按工具粒度配置审批规则，支持流式中断与决策恢复。

### 13_multi_agent - 多 Agent 架构
- **Sub Agents**: 子 Agent 路由、工具包装、中央调度
- **Handoffs**: 基于状态的交接、基于子图的交接
- **Skills**: 渐进式技能披露系统
- **Router**: 问题分类路由分发

### 14_long_term_memory - 长期记忆
基于 InMemoryStore 的持久化键值存储，支持嵌入搜索。
