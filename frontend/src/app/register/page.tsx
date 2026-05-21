"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/providers/auth-provider";

const RECOVERY_QUESTIONS = [
  "你的第一位直属领导姓名是？",
  "你第一次独立负责的项目名称是？",
  "你最常用的备用联系方式后四位是？",
];

export default function RegisterPage() {
  const { register, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [password, setPassword] = useState("");
  const [recoveryQuestion, setRecoveryQuestion] = useState(RECOVERY_QUESTIONS[0]);
  const [recoveryAnswer, setRecoveryAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace("/");
    }
  }, [authLoading, isAuthenticated, router]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (
      !email.trim() ||
      !displayName.trim() ||
      !companyName.trim() ||
      !jobTitle.trim() ||
      !password ||
      !recoveryQuestion.trim() ||
      !recoveryAnswer.trim()
    ) {
      return;
    }

    setSubmitting(true);
    try {
      await register({
        email: email.trim(),
        password,
        display_name: displayName.trim(),
        company_name: companyName.trim(),
        job_title: jobTitle.trim(),
        recovery_question: recoveryQuestion.trim(),
        recovery_answer: recoveryAnswer.trim(),
      });
      router.replace("/");
    } catch (error) {
      toast({
        title: "注册失败",
        description:
          error instanceof Error ? error.message : "请稍后重试。",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading || isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-warm-accent border-t-transparent" />
          <p className="text-sm text-muted-foreground">正在验证登录状态...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-xl">
        <div className="page-header text-center mb-6">
          <h1 className="font-heading text-2xl font-bold text-warm-text">注册</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            创建账号并进入主流程工作台
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">邮箱</span>
              <Input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="your@email.com"
                required
                autoFocus
              />
            </label>

            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">姓名 / 昵称</span>
              <Input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                placeholder="请输入姓名或昵称"
                required
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">公司名称</span>
              <Input
                value={companyName}
                onChange={(event) => setCompanyName(event.target.value)}
                placeholder="请输入公司名称"
                required
              />
            </label>

            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">角色 / 职位</span>
              <Input
                value={jobTitle}
                onChange={(event) => setJobTitle(event.target.value)}
                placeholder="如：业务负责人 / 运营总监"
                required
              />
            </label>
          </div>

          <label className="flex flex-col gap-2 text-sm">
            <span className="font-medium">登录密码</span>
            <Input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="至少 6 位"
              required
              minLength={6}
            />
          </label>

          <div className="space-y-4 rounded-2xl border border-warm-border-light bg-warm-inset p-4">
            <div>
              <p className="text-sm font-medium text-warm-text">找回设置</p>
              <p className="mt-1 text-xs leading-6 text-muted-foreground">
                用于后续自助重置密码。
              </p>
            </div>

            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">找回问题</span>
              <select
                value={recoveryQuestion}
                onChange={(event) => setRecoveryQuestion(event.target.value)}
                className="input-field"
                required
              >
                {RECOVERY_QUESTIONS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">找回答案</span>
              <Input
                value={recoveryAnswer}
                onChange={(event) => setRecoveryAnswer(event.target.value)}
                placeholder="请输入便于记忆、但不易被猜到的答案"
                required
              />
            </label>
          </div>

          <Button type="submit" loading={submitting} className="w-full">
            {submitting ? "注册中..." : "注册并进入系统"}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            已有账号？{" "}
            <Link href="/login" className="text-primary hover:underline">
              去登录
            </Link>
          </p>
        </form>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          如果忘记密码，可在登录页通过安全问题自助找回。
        </p>

        <p className="mt-4 text-center">
          <Link
            href="/"
            className="text-sm text-muted-foreground transition-colors hover:text-warm-text"
          >
            返回首页
          </Link>
        </p>
      </div>
    </div>
  );
}
