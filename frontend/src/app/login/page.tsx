"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

type Role = "student" | "teacher";

export default function LoginPage() {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") ?? "/";

  const [role, setRole] = useState<Role>("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace(redirect);
    }
  }, [authLoading, isAuthenticated, router, redirect]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!password) return;
    setSubmitting(true);
    try {
      const loginEmail = role === "teacher" ? "teacher" : email.trim();
      if (role === "student" && !loginEmail) return;
      await login(loginEmail, password);
      router.replace(redirect);
    } catch (err) {
      toast({ title: "登录失败", description: err instanceof Error ? err.message : "请检查账户和密码", variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading || isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-warm-accent border-t-transparent" />
          <p className="text-sm text-muted-foreground">验证登录状态...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="page-header text-center mb-6">
          <h1 className="font-heading text-2xl font-bold text-warm-text">登录</h1>
          <p className="mt-2 text-sm text-muted-foreground">美太 AI 商业创新智能体</p>
        </div>

        {/* 角色切换 Tab */}
        <div className="flex gap-1 mb-6 p-1 bg-muted rounded-lg">
          <button
            type="button"
            onClick={() => { setRole("student"); setEmail(""); setPassword(""); }}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
              role === "student"
                ? "bg-background text-warm-text shadow-sm"
                : "text-muted-foreground hover:text-warm-text"
            }`}
          >
            学员
          </button>
          <button
            type="button"
            onClick={() => { setRole("teacher"); setPassword(""); }}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
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
                  onChange={(e) => setEmail(e.target.value)}
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
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="输入密码"
                  required
                  minLength={6}
                />
              </label>

              <Button type="submit" loading={submitting} className="w-full">
                {submitting ? "登录中..." : "登录"}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                还没有账号？{" "}
                <Link href="/register" className="text-primary hover:underline">
                  去注册
                </Link>
              </p>
            </>
          ) : (
            <>
              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">账户</span>
                <Input
                  value="teacher"
                  disabled
                  className="bg-muted text-muted-foreground cursor-not-allowed"
                />
              </label>

              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">密码</span>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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

        <p className="mt-6 text-center">
          <Link href="/" className="text-sm text-muted-foreground hover:text-warm-text transition-colors">
            返回首页
          </Link>
        </p>
      </div>
    </div>
  );
}
