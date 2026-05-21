"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { requestPasswordReset } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    try {
      await requestPasswordReset({ email: email.trim() });
      setSent(true);
      toast({
        title: "重置邮件已发送",
        description: "请检查邮箱，点击邮件中的链接重置密码。",
      });
    } catch (error) {
      toast({
        title: "发送失败",
        description: error instanceof Error ? error.message : "请稍后重试。",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6 text-center">
          <div className="space-y-2">
            <h1 className="font-heading text-2xl font-bold text-warm-text">
              邮件已发送
            </h1>
            <p className="text-sm text-muted-foreground">
              我们向 <span className="font-medium text-warm-text">{email}</span> 发送了一封密码重置邮件，请点击邮件中的链接完成重置。
            </p>
            <p className="text-xs text-muted-foreground">
              没有收到邮件？请检查垃圾邮件箱，或{" "}
              <button
                type="button"
                onClick={() => setSent(false)}
                className="text-primary hover:underline"
              >
                重新发送
              </button>
            </p>
          </div>
          <Link href="/login" className="text-sm text-primary hover:underline">
            返回登录
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
            找回密码
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            输入注册邮箱，我们将发送密码重置链接。
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <label className="flex flex-col gap-2 text-sm">
            <span className="font-medium">注册邮箱</span>
            <Input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="your@email.com"
              required
              autoFocus
            />
          </label>

          <Button type="submit" loading={loading} className="w-full">
            {loading ? "发送中..." : "发送重置邮件"}
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
