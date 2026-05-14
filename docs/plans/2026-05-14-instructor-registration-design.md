# 讲师账号注册完善 — 设计文档

**日期**: 2026-05-14
**状态**: 已确认
**方案**: A — 讲师工作台内创建

---

## 需求决策

| 决策 | 选择 |
|---|---|
| 讲师创建方式 | 讲师创建讲师（方案 A） |
| 种子账号 | 保留 `teacher` / `meitai123456` |
| 创建字段 | 邮箱 + 显示名称(选填) + 密码，自动 `role="instructor"` |

---

## 架构与数据流

```
前端
  InstructorDashboard 或 NavBar
    └─ "创建讲师" Button → Dialog
         ├─ 邮箱 (必填)
         ├─ 显示名称 (选填)
         ├─ 密码 (必填, ≥6位)
         └─ 提交 → POST /api/instructor/create-instructor
                      (Header: Bearer <instructor_token>)

后端
  POST /api/instructor/create-instructor
    ├─ require_instructor → 校验当前用户是 instructor
    ├─ CreateInstructorRequest (email, password, display_name)
    ├─ instructor_service.create_instructor(db, payload)
    │    ├─ 检查 email 唯一性（409 if exists）
    │    ├─ 创建 User(role="instructor")
    │    └─ 返回 UserResponse
    └─ 返回 201 + UserResponse
```

## 改动文件清单

| 层 | 文件 | 操作 |
|---|---|---|
| Schema | `backend/app/schemas/auth.py` | 新增 `CreateInstructorRequest` |
| Service | `backend/app/services/instructor_service.py` | 新增 `create_instructor()` |
| Route | `backend/app/api/routes/instructor.py` | 新增 `POST /create-instructor` |
| Test | `backend/tests/test_instructor_api.py` | 新增权限边界 + 正常路径测试 |
| Frontend API | `frontend/src/lib/api.ts` | 新增 `createInstructor()` |
| Frontend Types | `frontend/src/lib/types.ts` | 新增 `CreateInstructorRequest` |
| Frontend Component | `frontend/src/components/instructor-dashboard.tsx` | 添加创建按钮 + Dialog |
| 注册页 | `frontend/src/app/register/page.tsx` | 不动 |
| 登录页 | `frontend/src/app/login/page.tsx` | 不动 |

## 错误处理

| 场景 | HTTP | 响应 |
|---|---|---|
| 无 token / token 过期 | 401 | "认证信息无效或已过期，请重新登录。" |
| 当前用户不是讲师 | 403 | "仅讲师可访问此功能。" |
| 邮箱已被注册 | 409 | "该邮箱已被注册。" |
| 密码 < 6 位 | 422 | Pydantic 自动校验 |
| 邮箱格式非法 | 422 | Pydantic 自动校验 |
| 网络异常 | — | toast 提示重试 |
| 403 (前端) | — | toast 提示权限不足 |

## 测试策略

### 后端 — 权限边界

- `test_create_instructor_as_student_returns_403`
- `test_dashboard_as_student_returns_403`
- `test_batch_comment_as_student_returns_403`
- `test_export_as_student_returns_403`
- `test_unauthenticated_returns_401`

### 后端 — 正常路径

- `test_create_instructor_success` → 201 + role="instructor"
- `test_create_instructor_duplicate_email` → 409
- `test_create_instructor_weak_password` → 422
- `test_seed_teacher_can_create_instructor` → 201

### 前端 — 权限边界（手动验证）

- [ ] 学生登录 → 不显示"创建讲师"按钮
- [ ] 学生登录 → 不显示 InstructorDashboard
- [ ] 学生登录 → 页面无 403 console/network 报错
- [ ] 讲师登录 → 显示"创建讲师"按钮
- [ ] 未登录 → 所有讲师入口不可见

### Smoke Pipeline

每次改动后运行：Backend Health → Frontend Root → Frontend Proxy → CORS Preflight → Browser Fetch

---

## 硬编码种子账号（保持不变）

```python
TEACHER_EMAIL = "teacher"
TEACHER_PASSWORD = "meitai123456"
```

首次启动时种子讲师自动创建（role="instructor"），用此账号创建更多讲师。

## 不做的

- 不做完整的讲师 CRUD 列表管理（后续按需添加）
- 不改变公开注册页面
- 不改变登录页面
- 不引入新的角色类型（如 superadmin）
