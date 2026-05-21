"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { resetPasswordByToken } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

function ResetPasswordPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!token || !newPassword) return;

    setLoading(true);
    try {
      await resetPasswordByToken({ token, new_password: newPassword });
      setDone(true);
      toast({
        title: "密码已重置",
        description: "请使用新密码重新登录。",
      });
    } catch (error) {
      toast({
        title: "重置失败",
        description: error instanceof Error ? error.message : "请稍后重试。",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6 text-center">
          <h1 className="font-heading text-2xl font-bold text-warm-text">
            无效的重置链接
          </h1>
          <p className="text-sm text-muted-foreground">
            缺少重置 token，请确认链接完整或重新申请找回密码。
          </p>
          <Link href="/forgot-password" className="text-sm text-primary hover:underline">
            重新申请
          </Link>
        </div>
      </div>
    );
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6 text-center">
          <div className="space-y-2">
            <h1 className="font-heading text-2xl font-bold text-warm-text">
              密码已重置
            </h1>
            <p className="text-sm text-muted-foreground">
              新密码已生效，请使用新密码登录。
            </p>
          </div>
          <Link href="/login" className="text-sm text-primary hover:underline">
            去登录
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="page-header text-center mb-6">
          <h1 className="font-heading text-2xl font-bold text-warm-text">
            设置新密码
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            请输入你的新密码。
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <label className="flex flex-col gap-2 text-sm">
            <span className="font-medium">新密码</span>
            <Input
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="至少 6 位"
              minLength={6}
              required
              autoFocus
            />
          </label>

          <Button type="submit" loading={loading} className="w-full">
            {loading ? "重置中..." : "确认重置"}
          </Button>
        </form>

        <p className="mt-6 text-center">
          <Link
            href="/login"
            className="text-sm text-muted-foreground transition-colors hover:text-warm-text"
          >
            返回登录
          </Link>
        </p>
      </div>
    </div>
  );
}

function ResetPasswordPageFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-4 text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-warm-accent border-t-transparent" />
        <p className="text-sm text-muted-foreground">加载中...</p>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<ResetPasswordPageFallback />}>
      <ResetPasswordPageContent />
    </Suspense>
  );
}
