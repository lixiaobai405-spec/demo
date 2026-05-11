"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

export default function RegisterPage() {
  const { register, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace("/");
    }
  }, [authLoading, isAuthenticated, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password) return;
    setSubmitting(true);
    try {
      await register(email.trim(), password, displayName.trim() || undefined);
      router.replace("/");
    } catch (err) {
      toast({ title: "注册失败", description: err instanceof Error ? err.message : "请稍后重试", variant: "destructive" });
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
          <h1 className="font-heading text-2xl font-bold text-warm-text">注册</h1>
          <p className="mt-2 text-sm text-muted-foreground">创建账号开始使用</p>
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
            <span className="font-medium">显示名称（选填）</span>
            <Input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="你的名字"
            />
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="font-medium">密码（至少 6 位）</span>
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
            {submitting ? "注册中..." : "注册"}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            已有账号？{" "}
            <Link href="/login" className="text-primary hover:underline">
              去登录
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
