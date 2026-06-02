# Current Status

最后更新：2026-05-05

## 项目概述

美太 AI 商业创新智能体 Demo — 一套完整的咨询式 SaaS 工具，帮助企业通过结构化流程完成从问卷到课后跟进的 AI 创新规划。

**14 步完整链路**：企业问卷 → 企业画像 → 商业画布 9 格诊断 → 突破要素推荐 → 创新方向延展 → 差异化竞争力分析 → 商业终局设计 → AI 场景推荐 → 分层案例匹配 → 报告生成（14 章节） → 多格式导出 → 课后 30 天跟进 → 双周案例推送 → 讲师工作台

## 项目进展总览

| 阶段 | 进度 | 状态 |
|------|:---:|:---:|
| 阶段 A 夯实 Demo | 100% | ✅ |
| 阶段 B V2 方法论流程 | 100% | ✅ |
| 阶段 C 知识库与质量 | 95% | ✅ |
| 阶段 D 课后跟进与运营 | 95% | ✅ |
| 阶段 E 前端视觉升级 | 100% | ✅ |
| **整体** | **~97%** | |

## 已完成功能

### 阶段 A — Demo 基础
- [x] FastAPI + Next.js 15 项目骨架
- [x] SQLite 持久化 + SQLAlchemy 2.0 ORM（所有模型自动建表）
- [x] 企业问卷 CRUD + 进度恢复 + refresh 回看
- [x] 课前导入工作台（文本/Markdown/表单/文件上传 + 自动预填 + 人工确认）
- [x] 企业画像生成（Mock 规则引擎 + LLM 可选）
- [x] 商业画布 9 格诊断（九要素问题库增强）
- [x] AI 场景推荐（方向加权规则评分）
- [x] 分层案例匹配（行业→规模→痛点→方向 + 来源标注 + 行业近亲映射）
- [x] 报告模板生成（14 章节固定结构）
- [x] 多格式导出：Markdown / DOCX / HTML / PDF / 打印版
- [x] LLM 报告增强（可选，失败自动回退模板）
- [x] RAG 检索模块（ChromaDB，默认关闭）
- [x] 质量审计系统（14 章节逐级评分 + 6 规则校验）
- [x] Docker Compose 一键部署

### 阶段 B — V2 方法论
- [x] 突破要素推荐 + 选择（9 要素评分，2-3 个可选手动调整）
- [x] 创新方向延展 + 选择（每要素 6 方向，勾选 1-6 个）
- [x] 差异化竞争力分析（VP 重构 + 点到线串联 + 核心优势 + 壁垒评级 + 三阶段推进）
- [x] 商业终局设计（私域 + 生态 + OPC + 3 路径推演 + 投资需求）
- [x] 全模块级联清空机制（上游重新生成时下游自动失效）
- [x] 方向加权场景推荐

### 阶段 C — 知识库与质量
- [x] 九要素问题库（9 格 × 26 问题类别 × 81 症状）
- [x] 分层案例检索（行业 → 规模 → 痛点 → 方向）
- [x] 质量审计系统（14 章节评分 + 6 规则）
- [x] 商业终局知识库（4 行业模板）
- [x] 行业近亲映射（14 个行业家族）

### 阶段 D — 课后跟进
- [x] 课后 30 天跟进（6 项默认任务 + 4 态流转：待启动/进行中/已完成/已阻塞 + 进展备注）
- [x] 双周案例推送（去重 + 6 轮次学习笔记 + 方案再校准）
- [x] 讲师工作台（分组筛选 + 批量点评 + 完成率统计 + CSV 导出）
- [x] 学员/讲师双视角切换

### 阶段 E — 前端视觉升级（2026-05-05 完成）
- [x] 全局暖色调设计系统：CSS 变量体系（暖奶油底 + 琥珀点缀 + 纸张纹理）
- [x] 字体升级：Noto Serif SC 宋体标题 + PingFang SC 正文 + JetBrains Mono 等宽
- [x] 卡片质感：玻璃拟物 → 纸面投射阴影
- [x] 24 文件统一改造（7 页面 + 14 组件 + 3 系统文件）
- [x] 共享组件样式类（card / page-header / btn-* / badge / input-field 等）
- [x] Stagger 入场动画
- [x] CORS 修复：添加 192.168.112.1 来源
- [x] 前端 `.env.local` 配置创建

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 后端框架 | FastAPI | - |
| ORM | SQLAlchemy | 2.0.44 |
| 数据库 | SQLite | - |
| 向量检索 | ChromaDB | 可选 |
| 前端框架 | Next.js | 15.5.9 |
| UI | React | 18.2.0 |
| 样式 | Tailwind CSS | 3.4.7 + 自定义 CSS 变量 |
| 字体 | Noto Serif SC / PingFang SC / JetBrains Mono | Google Fonts CDN |
| 报告导出 | python-docx / markdown | - |
| 容器化 | Docker Compose | - |

## 运行环境

| 组件 | 端口 | 启动方式 |
|------|:---:|------|
| 后端 | 8000 | `source /e/Anaconda3/Scripts/activate && conda activate meitai-project && python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload` |
| 前端 | 3001 | `cd frontend && npx next dev -p 3001` |
| Docker | 8000 + 3001 | `docker-compose up` |

**重要**：后端必须在 conda 环境 `meitai-project`（Python 3.11 + SQLAlchemy 2.0）下运行，系统默认 Python 3.7 不兼容。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_MODE` | `mock` | `mock` 走规则引擎；`live` 调用真实 LLM |
| `FRONTEND_ORIGIN` | `http://localhost:3001` | CORS 允许的前端地址 |
| `DATABASE_URL` | `sqlite:///./backend/data/meitai_demo.db` | SQLite 路径 |
| `RAG_ENABLED` | `false` | ChromaDB 向量检索开关 |
| `LLM_REPORT_ENABLED` | `false` | LLM 增强报告开关 |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | 前端调用后端地址 |
| `INTAKE_MAX_UPLOAD_SIZE_MB` | `10` | 导入文件大小上限 |

CORS 当前允许的来源（`backend/app/main.py`）：
- `http://localhost:3001`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`
- `http://192.168.112.1:3001`

## API 端点

### 核心流程（14 步）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/assessments` | 创建问卷 |
| `GET` | `/api/assessments/{id}` | 聚合状态（含 profile/canvas/breakthrough/scenarios/cases/report） |
| `POST` | `/api/assessments/{id}/profile` | 生成企业画像 |
| `POST` | `/api/assessments/{id}/canvas` | 画布 9 格诊断 |
| `POST` | `/api/assessments/{id}/breakthrough/recommend` | 突破要素推荐 |
| `POST` | `/api/assessments/{id}/breakthrough/select` | 突破要素选择 |
| `POST` | `/api/assessments/{id}/directions/expand` | 方向延展 |
| `POST` | `/api/assessments/{id}/directions/select` | 方向选择 |
| `POST` | `/api/assessments/{id}/competitiveness/generate` | 竞争力分析 |
| `POST` | `/api/assessments/{id}/endgame/generate` | 商业终局分析 |
| `POST` | `/api/assessments/{id}/scenarios` | 场景推荐 |
| `POST` | `/api/assessments/{id}/cases` | 案例匹配 |
| `POST` | `/api/assessments/{id}/report?mode=template\|llm` | 生成报告 |

### 报告与导出

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/reports/{id}` | 报告详情 |
| `GET` | `/api/reports/{id}/export/markdown` | 下载 Markdown |
| `GET` | `/api/reports/{id}/export/docx` | 下载 DOCX |
| `GET` | `/api/reports/{id}/export/pdf` | 下载 PDF |
| `GET` | `/api/reports/{id}/print` | 打印版 HTML |
| `GET` | `/api/reports/{id}/enrich` | 报告增强 |
| `GET` | `/api/reports/{id}/quality` | 质量审计报告 |
| `POST` | `/api/reports/{id}/share` | 生成分享链接 |

### 课后跟进 + 讲师视角

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/assessments/{id}/follow-up` | 跟进计划 |
| `PATCH` | `/api/assessments/{id}/follow-up/tasks/{task_id}` | 更新任务状态 |
| `POST` | `/api/assessments/{id}/push` | 双周案例推送 |
| `POST` | `/api/assessments/{id}/recalibrate` | 方案再校准 |
| `GET` | `/api/instructor/dashboard` | 讲师仪表盘 |
| `POST` | `/api/instructor/batch-comment` | 批量点评 |
| `GET` | `/api/instructor/export?format=csv` | CSV 导出 |

### 课前导入

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/intake/import` | 导入文本/Markdown/表单 |
| `POST` | `/api/intake/import/file` | 上传文件导入（PDF/DOCX/TXT/MD） |
| `GET` | `/api/intake/import/{session_id}` | 查看导入会话详情 |
| `POST` | `/api/intake/import/{session_id}/assessment` | 从导入会话正式创建问卷 |

## 前端页面

| 路由 | 说明 |
|------|------|
| `/` | 首页（健康检查 + 功能链路 + 入口按钮） |
| `/assessment` | 问卷工作台（学员/讲师双视角） |
| `/assessment/{id}` | 指定问卷回看（状态恢复 + 继续生成） |
| `/intake` | 课前材料导入工作台 |
| `/report/{id}` | 报告生成页（前置条件检查 + 模板/LLM 选择） |
| `/report-context/{id}` | 报告上下文预览（JSON 原始数据） |
| `/reports/{id}` | 富文本报告预览（HTML + 导出 + 元信息） |

## 数据库模型

所有表由 SQLAlchemy `Base.metadata.create_all()` 自动创建：

| 表 | 说明 |
|----|------|
| `assessments` | 企业问卷（11 字段 + 进度状态） |
| `canvas_diagnosis` | 画布 9 格诊断结果 |
| `breakthrough_selections` | 突破要素选择记录 |
| `direction_selections` | 创新方向选择记录 |
| `competitiveness_analyses` | 竞争力分析结果 |
| `endgame_analyses` | 商业终局分析结果 |
| `scenario_recommendations` | AI 场景推荐 |
| `case_recommendations` | 案例匹配结果 |
| `generated_reports` | 报告（含 HTML/Markdown/JSON + 质量评分 + 导出路径） |
| `follow_up_tasks` | 课后跟进任务 |
| `push_records` | 双周推送记录 |
| `assessment_intake_sessions` | 课前导入会话 |

## 报告结构

模板报告固定 14 章节：
1. 企业基本画像
2. 当前商业模式画布诊断
3. 突破要素
4. 创新方向延展
5. AI 成熟度评估
6. 高优先级 AI 提效场景
7. 推荐场景详细规划
8. 差异化竞争力设计
9. 参考案例与启示
10. 三阶段 AI 创新路线图
11. 90 天行动计划
12. 风险与阻力
13. 讲师点评区
14. 商业终局设计

## 测试基准

### 后端

```bash
cd backend
conda run -n meitai-project python -m pytest tests/ -v
# 19 passed, 1 skipped (4.51s)
```

- `test_api_intake_flow.py` — 11 tests（导入全流程：文本/文件/表单/错误处理/去重）
- `test_api_main_flow.py` — 7 tests + 1 skipped（健康检查/模板报告/LLM 回退/案例自动匹配/向后兼容）
- `test_e2e_full_chain.py` — 1 test（26 步骤全链路：画像→画布→突破→方向→竞争力→终局→场景→案例→报告→导出→分享→跟进→推送→讲师→级联清空）

### 前端

```bash
cd frontend
npx vitest run
# 1 test file, 6 tests passed (2.70s)
```

- `intake-workbench.test.tsx` — 6 tests（导入工作台组件渲染和交互）

## 运行模式

| 模式 | 配置 | 说明 |
|------|------|------|
| Mock（默认） | `LLM_MODE=mock` | 所有生成走规则引擎/模板，无需 API Key，确定性输出 |
| Live | `LLM_MODE=live` + API Key | 画像/画布/报告可走真实 LLM |
| 报告：模板 | `mode=template` | 始终使用固定模板生成报告 |
| 报告：LLM | `mode=llm` | 尝试 LLM 增强，失败/超时自动回退模板 |

## 设计系统（2026-05-05 更新）

| 维度 | 配置 |
|------|------|
| 底色 | 暖奶油 `#FDFBF7` → `#F5EFE4` + 纸张纤维纹理 |
| 主色 | 暖琥珀 `#B8752A` |
| 语义色：成功/警告/危险 | 橄榄绿 `#7A9A5C` / 暖橙 `#C8842A` / 陶土红 `#C0564A` |
| 标题字体 | Noto Serif SC（思源宋体） |
| 正文字体 | PingFang SC |
| 等宽字体 | JetBrains Mono |
| 卡片 | 暖白底 `#FFFDF9` + 纸面阴影 |
| 按钮 | 统一 pill 圆角 + 琥珀填充/描边/成功三态 |
| 圆角 | `0.5rem` ~ `1.25rem`（比之前大幅减小，更精致） |

## 当前已知问题

| # | 问题 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 端口 3000 残留兼容 | 低优 | CORS 仍保留 3000 端口，frontend 已固定在 3001 |
| 2 | 真实 LLM 端到端验证 | 待做 | 需配 OpenAI API Key |
| 3 | 课堂并发压测 | 待做 | 20-50 人场景未验证 |
| 4 | 前端测试覆盖不足 | 已知 | 仅 intake-workbench 有 6 个组件测试，其余页面依赖手动验证 |
| 5 | RAG 默认关闭 | 设计如此 | 启用需配置 ChromaDB + Embedding |
| 6 | `NEXT_PUBLIC_API_BASE_URL` 显示 "not set" | 低优 | `.env.local` 已创建，Next.js 缓存可能导致首次显示为空，刷新后正常 |

## 2026-05-05 变更记录

### 前端视觉升级
- 全局暖色调设计系统：`globals.css` 完全重写
- `tailwind.config.ts` 扩展 warm 色板 + 字体
- `layout.tsx` 引入 Google Fonts（Noto Serif SC / JetBrains Mono）
- 7 个页面 + 14 个组件全部改造为暖调编辑室风格
- 共享组件样式类（card / page-header / btn-* / badge / input-field / section-label 等）
- Stagger 入场动画
- 净减少 ~1,700 行代码（移除 Tailwind 内联重复）

### 后端修复
- CORS 添加 `http://192.168.112.1:3001` 来源
- `assessments.py` walrus operator 展开（Python 3.7 兼容，meitai-project 3.11 不需要但保留）
- `.env` + `.env.local` 创建

### 验证通过
- TypeScript 类型检查 ✅
- Next.js 构建（8 路由） ✅
- 后端测试 19/20 ✅
- 前端测试 6/6 ✅
- 后端 health check ✅
- CORS 跨域请求 ✅
