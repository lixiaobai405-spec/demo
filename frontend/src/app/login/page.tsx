"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

export default function LoginPage() {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") ?? "/";

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
    if (!email.trim() || !password) return;
    setSubmitting(true);
    try {
      await login(email.trim(), password);
      router.replace(redirect);
    } catch (err) {
      toast({ title: "登录失败", description: err instanceof Error ? err.message : "请检查邮箱和密码", variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading || isAuthenticated) {
    return <div className="min-h-screen" />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="page-header text-center mb-6">
          <h1 className="font-heading text-2xl font-bold text-warm-text">登录</h1>
          <p className="mt-2 text-sm text-muted-foreground">美太 AI 商业创新智能体</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
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
