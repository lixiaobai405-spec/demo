# 讲师创建讲师 — 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use godmode:task-runner to implement this plan task-by-task.

**Goal:** 已登录讲师在前端 Dialog 中创建新讲师账号（邮箱 + 显示名称 + 密码），后端 require_instructor 保护。

**Architecture:** 后端新增 `POST /api/instructor/create-instructor` 端点，调用 `InstructorService.create_instructor()`；前端在 InstructorDashboard 加"创建讲师"按钮 + Dialog 表单。

**Tech Stack:** Python FastAPI + SQLAlchemy + bcrypt + python-jose；Next.js + React + shadcn/ui + Zustand

---

## 文件改动总览

| 文件 | 操作 |
|---|---|
| `backend/app/schemas/auth.py` | 修改 — 新增 CreateInstructorRequest |
| `backend/app/services/instructor_service.py` | 修改 — 新增 create_instructor() |
| `backend/app/api/routes/instructor.py` | 修改 — 新增 POST /create-instructor |
| `backend/tests/test_instructor_api.py` | 新建 — 权限边界 + 正常路径测试 |
| `frontend/src/lib/types.ts` | 修改 — 新增 CreateInstructorRequest |
| `frontend/src/lib/api.ts` | 修改 — 新增 createInstructor() |
| `frontend/src/components/instructor-dashboard.tsx` | 修改 — 添加创建按钮 + Dialog |

---

### Task 1: 后端 Schema — CreateInstructorRequest

**Files:**
- Modify: `backend/app/schemas/auth.py`

**Step 1: 添加 schema**

在 `RegisterRequest` 类后面添加：

```python
class CreateInstructorRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)
```

**Step 2: 验证**

```bash
cd backend && python -c "from app.schemas.auth import CreateInstructorRequest; print('OK')"
```

预期: OK

**Step 3: Commit**

```bash
git add backend/app/schemas/auth.py
git commit -m "feat: add CreateInstructorRequest schema for instructor creation"
```

---

### Task 2: 后端 Service — create_instructor()

**Files:**
- Modify: `backend/app/services/instructor_service.py`

**Step 1: 在 InstructorService 类中添加方法**

```python
from app.models.user import User
from app.schemas.auth import CreateInstructorRequest, UserResponse
from app.services.auth_service import _hash_password
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class InstructorService:
    # ... 现有方法保持不变 ...

    def create_instructor(self, db: Session, request: CreateInstructorRequest) -> UserResponse:
        existing = db.query(User).filter(User.email == request.email).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该邮箱已被注册。",
            )

        user = User(
            email=request.email,
            hashed_password=_hash_password(request.password),
            display_name=request.display_name,
            role="instructor",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user, from_attributes=True)
```

**Step 2: 验证**

```bash
cd backend && python -c "from app.services.instructor_service import InstructorService; print('OK')"
```

预期: OK

**Step 3: Commit**

```bash
git add backend/app/services/instructor_service.py
git commit -m "feat: add create_instructor method to InstructorService"
```

---

### Task 3: 后端 Route — POST /create-instructor

**Files:**
- Modify: `backend/app/api/routes/instructor.py`

**Step 1: 在现有路由后面添加端点**

```python
from app.schemas.auth import CreateInstructorRequest, UserResponse

# 在 export_students 后面添加：

@router.post(
    "/create-instructor",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_instructor(
    payload: CreateInstructorRequest,
    db: Session = Depends(get_db),
    _instructor: User = Depends(require_instructor),
) -> UserResponse:
    service = InstructorService()
    return service.create_instructor(db, payload)
```

**Step 2: 验证路由注册**

```bash
cd backend && python -c "from app.api.router import api_router; print('OK')"
```

预期: OK

**Step 3: Commit**

```bash
git add backend/app/api/routes/instructor.py
git commit -m "feat: add POST /api/instructor/create-instructor endpoint"
```

---

### Task 4: 后端测试 — 权限边界 + 正常路径

**Files:**
- Create: `backend/tests/test_instructor_api.py`

**Step 1: 写测试**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.services.auth_service import _hash_password

client = TestClient(app)


def _get_token(client, email, password="test123456"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return None
    return resp.json()["access_token"]


# ── 权限边界 ──

def test_create_instructor_unauthenticated_returns_401():
    resp = client.post("/api/instructor/create-instructor", json={
        "email": "new_teacher@test.com", "password": "123456"
    })
    assert resp.status_code == 401


def test_create_instructor_as_student_returns_403():
    student_token = _get_token(client, "student_for_test@example.com", "test123456")
    if student_token is None:
        resp = client.post("/api/auth/register", json={
            "email": "student_for_test@example.com",
            "password": "test123456",
            "display_name": "Test Student"
        })
        assert resp.status_code == 201
        student_token = resp.json()["access_token"]

    resp = client.post(
        "/api/instructor/create-instructor",
        json={"email": "should_fail@test.com", "password": "123456"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403


def test_dashboard_as_student_returns_403():
    student_token = _get_token(client, "student_for_test@example.com", "test123456")
    if student_token is None:
        resp = client.post("/api/auth/register", json={
            "email": "student_for_test@example.com",
            "password": "test123456",
        })
        assert resp.status_code == 201
        student_token = resp.json()["access_token"]

    resp = client.get(
        "/api/instructor/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403


def test_batch_comment_as_student_returns_403():
    student_token = _get_token(client, "student_for_test@example.com", "test123456")
    if student_token is None:
        resp = client.post("/api/auth/register", json={
            "email": "student_for_test@example.com",
            "password": "test123456",
        })
        assert resp.status_code == 201
        student_token = resp.json()["access_token"]

    resp = client.post(
        "/api/instructor/batch-comment",
        json={"assessment_ids": [], "comment": "test"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403


def test_export_as_student_returns_403():
    student_token = _get_token(client, "student_for_test@example.com", "test123456")
    if student_token is None:
        resp = client.post("/api/auth/register", json={
            "email": "student_for_test@example.com",
            "password": "test123456",
        })
        assert resp.status_code == 201
        student_token = resp.json()["access_token"]

    resp = client.get(
        "/api/instructor/export?format=csv",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403


# ── 正常路径 ──

def test_seed_teacher_can_create_instructor():
    # 用种子账号登录
    resp = client.post("/api/auth/login", json={
        "email": "teacher", "password": "meitai123456"
    })
    assert resp.status_code == 200
    teacher_token = resp.json()["access_token"]

    resp = client.post(
        "/api/instructor/create-instructor",
        json={
            "email": f"new_instructor_{pytest.importorskip('uuid').uuid4().hex[:8]}@test.com",
            "password": "secure123",
            "display_name": "新讲师"
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "instructor"
    assert data["display_name"] == "新讲师"


def test_create_instructor_duplicate_email():
    resp = client.post("/api/auth/login", json={
        "email": "teacher", "password": "meitai123456"
    })
    teacher_token = resp.json()["access_token"]

    # 第一次创建
    email = "duplicate_teacher@test.com"
    client.post(
        "/api/instructor/create-instructor",
        json={"email": email, "password": "123456"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    # 第二次应冲突
    resp = client.post(
        "/api/instructor/create-instructor",
        json={"email": email, "password": "123456"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert resp.status_code == 409


def test_create_instructor_weak_password():
    resp = client.post("/api/auth/login", json={
        "email": "teacher", "password": "meitai123456"
    })
    teacher_token = resp.json()["access_token"]

    resp = client.post(
        "/api/instructor/create-instructor",
        json={"email": "weakpw@test.com", "password": "12345"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert resp.status_code == 422
```

**Step 2: 运行测试验证失败/通过**

```bash
cd backend && python -m pytest tests/test_instructor_api.py -v
```

预期: 8 tests PASS (seed teacher 创建 + 权限边界全绿)

**Step 3: Commit**

```bash
git add backend/tests/test_instructor_api.py
git commit -m "test: add instructor API permission boundary and creation tests"
```

---

### Task 5: 前端 Types — CreateInstructorRequest

**Files:**
- Modify: `frontend/src/lib/types.ts`

**Step 1: 在 Auth 类型区域添加**

紧接 `RegisterRequest` 之后：

```typescript
export type CreateInstructorRequest = {
  email: string;
  password: string;
  display_name?: string | null;
};
```

**Step 2: 验证 TypeScript**

```bash
cd frontend && npx tsc --noEmit --pretty 2>&1 | head -20
```

预期: 无新增类型错误

**Step 3: Commit**

```bash
git add frontend/src/lib/types.ts
git commit -m "feat: add CreateInstructorRequest type"
```

---

### Task 6: 前端 API — createInstructor()

**Files:**
- Modify: `frontend/src/lib/api.ts`

**Step 1: 在 `instructorExportCsv` 之后添加函数**

```typescript
export function createInstructor(payload: CreateInstructorRequest): Promise<UserResponse> {
  return fetch(`${apiBaseUrl}/api/instructor/create-instructor`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload),
  }).then(async (res) => {
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail ?? "创建讲师失败");
    return data;
  });
}
```

记得在文件顶部 import 中添加 `CreateInstructorRequest`。

**Step 2: 验证**

```bash
cd frontend && npx tsc --noEmit --pretty 2>&1 | head -20
```

预期: 无新增类型错误

**Step 3: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add createInstructor API function"
```

---

### Task 7: 前端 UI — 创建讲师按钮 + Dialog

**Files:**
- Modify: `frontend/src/components/instructor-dashboard.tsx`

**Step 1: 添加导入、状态和 Dialog UI**

在文件顶部添加 import：

```typescript
import { createInstructor } from "@/lib/api";
```

在 `InstructorDashboard` 组件中添加状态（在 `commentStatus` 之后）：

```typescript
const [showCreateDialog, setShowCreateDialog] = useState(false);
const [newEmail, setNewEmail] = useState("");
const [newPassword, setNewPassword] = useState("");
const [newName, setNewName] = useState("");
const [creating, setCreating] = useState(false);
const [createError, setCreateError] = useState<string | null>(null);
```

添加创建处理函数（在 `handleExport` 之后）：

```typescript
async function handleCreateInstructor(e: React.FormEvent) {
  e.preventDefault();
  if (!newEmail.trim() || !newPassword) return;
  setCreating(true);
  setCreateError(null);
  try {
    await createInstructor({
      email: newEmail.trim(),
      password: newPassword,
      display_name: newName.trim() || undefined,
    });
    setShowCreateDialog(false);
    setNewEmail("");
    setNewPassword("");
    setNewName("");
    toast({ title: "创建成功", description: `讲师 ${newEmail} 已创建。` });
  } catch (err) {
    setCreateError(err instanceof Error ? err.message : "创建失败");
  } finally {
    setCreating(false);
  }
}
```

在标题栏"导出 CSV"按钮旁添加"创建讲师"按钮：

```tsx
<button type="button" onClick={() => setShowCreateDialog(true)}
  className="btn-primary text-xs">创建讲师</button>
```

在 `return` 的 `</div>` 最后（card 闭合前）添加 Dialog：

```tsx
{showCreateDialog && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    onClick={() => { setShowCreateDialog(false); setCreateError(null); }}>
    <form
      className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md space-y-4"
      onClick={(e) => e.stopPropagation()}
      onSubmit={handleCreateInstructor}
    >
      <h3 className="font-heading text-lg font-bold text-warm-text">创建讲师账号</h3>

      {createError && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{createError}</div>
      )}

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">邮箱</span>
        <Input
          type="email"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          placeholder="instructor@example.com"
          required
          autoFocus
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">显示名称（选填）</span>
        <Input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="张老师"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">密码（至少 6 位）</span>
        <Input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder="输入密码"
          required
          minLength={6}
        />
      </label>

      <div className="flex gap-3 justify-end pt-2">
        <Button type="button" variant="outline"
          onClick={() => { setShowCreateDialog(false); setCreateError(null); }}>
          取消
        </Button>
        <Button type="submit" loading={creating}>
          {creating ? "创建中..." : "创建讲师"}
        </Button>
      </div>
    </form>
  </div>
)}
```

**Step 2: 验证 TypeScript**

```bash
cd frontend && npx tsc --noEmit --pretty 2>&1 | head -20
```

预期: 无新增类型错误

**Step 3: Commit**

```bash
git add frontend/src/components/instructor-dashboard.tsx
git commit -m "feat: add create-instructor button and dialog to instructor dashboard"
```

---

### Task 8: 端到端验证

**Step 1: 启动后端测试**

```bash
cd backend && python -m pytest tests/test_instructor_api.py -v
```

预期: 8 tests PASS

**Step 2: Smoke pipeline**

```bash
python tools/smoke_pipeline.py --frontend http://127.0.0.1:5173 --backend http://127.0.0.1:8000 --backend-health /health --frontend-proxy /api/health
```

预期: All PASS or at least Backend/PROXY/CORS PASS

**Step 3: 手动验证清单**

- [ ] 学生登录 → `POST /api/instructor/create-instructor` → 403
- [ ] 学生登录 → 页面不显示"创建讲师"按钮
- [ ] 学生登录 → console/network 无 403 报错
- [ ] 讲师登录（teacher / meitai123456）→ 看到"创建讲师"按钮
- [ ] 讲师创建新讲师 → 成功 toast
- [ ] 新讲师登录 → 角色为 instructor，可访问仪表盘
- [ ] 重复邮箱 → "该邮箱已被注册"错误

**Step 4: Commit（如有微调）**

```bash
git add -A && git status
git commit -m "chore: final E2E verification adjustments"
```
