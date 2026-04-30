# Current Status

最后更新：2025-06-29

## 项目进展总览

| 阶段 | 进度 | 状态 |
|------|:---:|:---:|
| 阶段 A 夯实 Demo | 85% | ✅ |
| 阶段 B V2 方法论流程 | 95% | ✅ |
| 阶段 C 知识库与质量 | 85% | ✅ |
| 阶段 D 课后跟进与运营 | 90% | ✅ |
| **整体** | **~90%** | |

## 已完成功能

### 阶段 A — Demo 基础
- [x] FastAPI + Next.js 项目骨架
- [x] SQLite 持久化 + 所有模型自建表
- [x] 企业问卷 CRUD + 进度恢复
- [x] 课前导入（PDF/DOCX 解析 + 自动预填）
- [x] 企业画像（Mock + LLM）
- [x] 商业画布 9 格诊断
- [x] AI 场景推荐（规则评分）
- [x] 案例匹配
- [x] 报告模板生成 + Markdown/DOCX/打印版导出
- [x] LLM 报告增强 + 失败自动回退模板
- [x] RAG 检索模块（默认关闭）
- [x] 后端全链路自动化测试 (19 passed, 1 skipped)

### 阶段 B — V2 方法论
- [x] 突破要素推荐 + 选择（9 要素评分）
- [x] 创新方向延展 + 选择（6 方向/要素）
- [x] 差异化竞争力分析（VP 重构 + 点到线串联 + 4 象限策略）
- [x] 商业终局设计（私域 + 生态 + OPC + 3 路径推演）
- [x] 全模块级联清空机制
- [x] 方向加权场景推荐

### 阶段 C — 知识库与质量
- [x] 九要素问题库（9 格 × 26 问题类别 × 81 症状）
- [x] 分层案例检索（行业→规模→痛点→方向 + 来源标注）
- [x] 质量审计系统（14 章节逐级评分 + 6 规则校验）
- [x] 商业终局知识库（4 行业模板）
- [x] 行业近亲映射（14 个行业家族）

### 阶段 D — 课后跟进
- [x] 课后 30 天跟进（6 项默认任务 + 4 态流转 + 进展备注 + 阻塞标记）
- [x] 双周案例推送（去重 + 6 轮次学习笔记 + 方案再校准）
- [x] 讲师工作台（分组筛选 + 批量点评 + CSV 导出）
- [x] 学员/讲师双视角切换

## 当前测试基准

```bash
cd backend
python -m pytest tests/ -v
# 19 passed, 1 skipped
```

E2E 全链路: `tests/test_e2e_full_chain.py` — 26 个步骤，涵盖从问卷到讲师工作台的完整链路。

## 环境配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| LLM_MODE | `mock` | 设为 `live` 启用真实 LLM |
| FRONTEND_ORIGIN | `http://localhost:3001` | 前端端口 |
| DATABASE_URL | `sqlite:///./backend/data/meitai_demo.db` | SQLite |
| RAG_ENABLED | `false` | RAG 默认关闭 |
| NEXT_PUBLIC_API_BASE_URL | `http://localhost:8000` | 前端调用后端地址 |

## 报告当前数据

- **14 章节**模板报告
- 质量评分 ~60/100（Mock 模式，随数据丰富度变化）
- Markdown 输出 ~12,000 字符
- DOCX 输出 ~47,000 bytes

## 端口说明

| 服务 | 端口 |
|------|:---:|
| 前端 | **3001** |
| 后端 | **8000** |

## 数据库模型

所有模型由 SQLAlchemy `create_all()` 自动建表：
- `assessments` — 企业问卷
- `canvas_diagnosis` — 画布诊断
- `breakthrough_selections` — 突破选择
- `direction_selections` — 方向选择
- `competitiveness_analyses` — 竞争力分析
- `endgame_analyses` — 商业终局
- `scenario_recommendations` — 场景推荐
- `case_recommendations` — 案例匹配
- `generated_reports` — 报告（含 quality_json）
- `follow_up_tasks` — 课后跟进
- `push_records` — 推送记录

## 当前 RAG 状态

- 默认关闭，路由前缀 `/rag`（非 `/api/rag`）
- 启用时支持向量检索 + 混合匹配（规则 + RAG）
- 支持 OpenAI 兼容 Embedding 或 Mock 降级

## 未完成任务

| # | 任务 | 优先级 |
|---|------|:---:|
| A1 | 端口严格统一 3001（CORS 仍带 3000 兼容） | 低 |
| LLM | 配真实 OpenAI Key 端到端验证 | 中 |
| Docker | 一键部署 (`docker-compose up`) | 中 |
| 压测 | 20-50 人课堂并发验证 | 中 |
| i18n | 多语言支持 | 低 |
