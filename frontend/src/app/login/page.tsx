"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";

import {
  formatMutationError,
  getForgotPasswordQuestion,
  resetPassword,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/providers/auth-provider";

type Role = "student" | "teacher";

function LoginPageContent() {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") ?? "/";

  const [role, setRole] = useState<Role>("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [recoveryEmail, setRecoveryEmail] = useState("");
  const [recoveryQuestion, setRecoveryQuestion] = useState("");
  const [recoveryAnswer, setRecoveryAnswer] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [questionLoading, setQuestionLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace(redirect);
    }
  }, [authLoading, isAuthenticated, redirect, router]);

  const loginEmail = useMemo(() => {
    if (role === "teacher") {
      return "teacher";
    }
    return email.trim();
  }, [email, role]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!password) return;
    if (role === "student" && !loginEmail) return;

    setSubmitting(true);
    try {
      await login(loginEmail, password);
    } catch (error) {
      toast({
        title: "登录失败",
        description:
          error instanceof Error ? error.message : "请检查账号和密码后重试。",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleLoadQuestion() {
    const targetEmail = recoveryEmail.trim() || email.trim();
    if (!targetEmail) {
      toast({
        title: "请输入邮箱",
        description: "请先输入注册邮箱，再获取找回问题。",
        variant: "destructive",
      });
      return;
    }

    setQuestionLoading(true);
    try {
      const result = await getForgotPasswordQuestion({ email: targetEmail });
      setRecoveryEmail(result.email);
      setRecoveryQuestion(result.recovery_question);
      toast({
        title: "找回问题已加载",
        description: "请输入答案并设置新密码。",
      });
    } catch (error) {
      toast({
        title: "获取失败",
        description: formatMutationError(error, "找回问题获取"),
        variant: "destructive",
      });
    } finally {
      setQuestionLoading(false);
    }
  }

  async function handleResetPassword(event: React.FormEvent) {
    event.preventDefault();
    if (!recoveryEmail.trim() || !recoveryQuestion || !recoveryAnswer.trim() || !newPassword) {
      return;
    }

    setResetLoading(true);
    try {
      await resetPassword({
        email: recoveryEmail.trim(),
        recovery_answer: recoveryAnswer.trim(),
        new_password: newPassword,
      });
      setPassword(newPassword);
      setShowForgotPassword(false);
      setRecoveryQuestion("");
      setRecoveryAnswer("");
      setNewPassword("");
      toast({
        title: "密码已重置",
        description: "请使用新密码重新登录。",
      });
    } catch (error) {
      toast({
        title: "重置失败",
        description: formatMutationError(error, "密码重置"),
        variant: "destructive",
      });
    } finally {
      setResetLoading(false);
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
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="page-header text-center mb-6">
          <h1 className="font-heading text-2xl font-bold text-warm-text">
            登录
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            美太 AI 商业创新智能体
          </p>
        </div>

        <div className="mb-6 flex gap-1 rounded-lg bg-muted p-1">
          <button
            type="button"
            onClick={() => {
              setRole("student");
              setEmail("");
              setPassword("");
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              role === "student"
                ? "bg-background text-warm-text shadow-sm"
                : "text-muted-foreground hover:text-warm-text"
            }`}
          >
            学员
          </button>
          <button
            type="button"
            onClick={() => {
              setRole("teacher");
              setPassword("");
              setShowForgotPassword(false);
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
              role === "teacher"
                ? "bg-background text-warm-text shadow-sm"
                : "text-muted-foreground hover:text-warm-text"
            }`}
          >
            讲师
          </button>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          {role === "student" ? (
            <>
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
                <span className="font-medium">密码</span>
                <Input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="输入密码"
                  required
                  minLength={6}
                />
              </label>

              <Button type="submit" loading={submitting} className="w-full">
                {submitting ? "登录中..." : "登录"}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                <button
                  type="button"
                  onClick={() => {
                    setRecoveryEmail(email.trim());
                    setShowForgotPassword((current) => !current);
                  }}
                  className="hover:underline"
                >
                  忘记密码？
                </button>{" "}
                <Link href="/forgot-password" className="text-primary hover:underline">
                  找回
                </Link>{" "}
                还没有账号？{" "}
                <Link href="/register" className="text-primary hover:underline">
                  去注册
                </Link>
              </p>
            </>
          ) : (
            <>
              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">账号</span>
                <Input
                  value="teacher"
                  disabled
                  className="cursor-not-allowed bg-muted text-muted-foreground"
                />
              </label>

              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">密码</span>
                <Input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="输入讲师密码"
                  required
                  autoFocus
                />
              </label>

              <Button type="submit" loading={submitting} className="w-full">
                {submitting ? "登录中..." : "讲师登录"}
              </Button>
            </>
          )}
        </form>

        {role === "student" && showForgotPassword ? (
          <section className="mt-4 space-y-4 rounded-2xl border border-warm-border bg-warm-surface p-4">
            <div>
              <p className="text-sm font-medium text-warm-text">自助找回密码</p>
              <p className="mt-1 text-xs leading-6 text-muted-foreground">
                输入注册邮箱，回答安全问题后即可重置密码。
              </p>
            </div>

            <form onSubmit={handleResetPassword} className="space-y-3">
              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">注册邮箱</span>
                <div className="flex gap-2">
                  <Input
                    type="email"
                    value={recoveryEmail}
                    onChange={(event) => setRecoveryEmail(event.target.value)}
                    placeholder="your@email.com"
                    required
                  />
                  <Button
                    type="button"
                    variant="outline"
                    loading={questionLoading}
                    onClick={handleLoadQuestion}
                  >
                    获取问题
                  </Button>
                </div>
              </label>

              {recoveryQuestion ? (
                <>
                  <div className="rounded-xl border border-warm-border-light bg-warm-inset px-4 py-3">
                    <p className="text-xs text-warm-muted">找回问题</p>
                    <p className="mt-1 text-sm text-warm-text">{recoveryQuestion}</p>
                  </div>

                  <label className="flex flex-col gap-2 text-sm">
                    <span className="font-medium">答案</span>
                    <Input
                      value={recoveryAnswer}
                      onChange={(event) => setRecoveryAnswer(event.target.value)}
                      placeholder="输入找回答案"
                      required
                    />
                  </label>

                  <label className="flex flex-col gap-2 text-sm">
                    <span className="font-medium">新密码</span>
                    <Input
                      type="password"
                      value={newPassword}
                      onChange={(event) => setNewPassword(event.target.value)}
                      placeholder="至少 6 位"
                      minLength={6}
                      required
                    />
                  </label>

                  <div className="flex flex-wrap gap-2">
                    <Button type="submit" loading={resetLoading}>
                      {resetLoading ? "重置中..." : "确认重置"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowForgotPassword(false);
                        setRecoveryQuestion("");
                        setRecoveryAnswer("");
                        setNewPassword("");
                      }}
                    >
                      取消
                    </Button>
                  </div>
                </>
              ) : null}
            </form>
          </section>
        ) : null}

        <section className="mt-6 rounded-2xl border border-warm-border bg-warm-surface p-4">
          <p className="text-center text-sm font-medium text-warm-text">
            需要帮助？
          </p>
          <p className="mt-2 text-center text-xs leading-6 text-muted-foreground">
            登录问题优先走上方自助找回；使用问题可联系下方咨询入口。
          </p>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="text-center">
              <Image
                src="/qrcodes/meitai-consulting-official-account.jpg"
                alt="美太咨询公众号"
                width={144}
                height={144}
                className="mx-auto rounded-lg"
              />
              <p className="mt-2 text-xs text-muted-foreground">
                美太咨询公众号
              </p>
            </div>
            <div className="text-center">
              <Image
                src="/qrcodes/meitai-usage-consulting.jpg"
                alt="使用咨询"
                width={144}
                height={144}
                className="mx-auto rounded-lg"
              />
              <p className="mt-2 text-xs text-muted-foreground">使用咨询</p>
            </div>
          </div>
        </section>

        <p className="mt-6 text-center">
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

function LoginPageFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-4 text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-warm-accent border-t-transparent" />
        <p className="text-sm text-muted-foreground">登录页加载中...</p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginPageFallback />}>
      <LoginPageContent />
    </Suspense>
  );
}
