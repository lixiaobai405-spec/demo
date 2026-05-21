"use client";

import { useState } from "react";
import Link from "next/link";

import { useAuth } from "@/providers/auth-provider";
import { updateRecovery } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

const RECOVERY_QUESTIONS = [
  "你的第一位直属领导姓名是？",
  "你第一次独立负责的项目名称是？",
  "你最常用的备用联系方式后四位是？",
];

export function NavBar() {
  const { isAuthenticated, user, isInstructor, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [recoveryOpen, setRecoveryOpen] = useState(false);
  const [recoveryQuestion, setRecoveryQuestion] = useState(RECOVERY_QUESTIONS[0]);
  const [recoveryAnswer, setRecoveryAnswer] = useState("");
  const [recoverySaving, setRecoverySaving] = useState(false);

  const showRecoveryHint = isAuthenticated && !isInstructor && user && !user.has_recovery;

  async function handleSaveRecovery(event: React.FormEvent) {
    event.preventDefault();
    if (!recoveryQuestion.trim() || !recoveryAnswer.trim()) return;
    setRecoverySaving(true);
    try {
      await updateRecovery({
        recovery_question: recoveryQuestion.trim(),
        recovery_answer: recoveryAnswer.trim(),
      });
      toast({ title: "找回设置已保存", description: "忘记密码时可通过安全问题自助找回。" });
      setRecoveryOpen(false);
      setRecoveryAnswer("");
    } catch (error) {
      toast({
        title: "保存失败",
        description: error instanceof Error ? error.message : "请稍后重试。",
        variant: "destructive",
      });
    } finally {
      setRecoverySaving(false);
    }
  }

  return (
    <nav className="sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="font-heading text-lg font-bold text-warm-text transition-colors hover:text-primary"
          >
            美太 AI
          </Link>
          <div className="hidden items-center gap-4 md:flex">
            <Link
              href="/"
              className="text-sm text-muted-foreground transition-colors hover:text-warm-text"
            >
              首页
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  href="/assessment"
                  className="text-sm text-muted-foreground transition-colors hover:text-warm-text"
                >
                  主流程工作台
                </Link>
                <Link
                  href="/history"
                  className="text-sm text-muted-foreground transition-colors hover:text-warm-text"
                >
                  评估历史
                </Link>
              </>
            ) : null}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="hidden items-center gap-3 md:flex">
              <span className="text-sm text-warm-text">
                {user?.display_name || user?.email}
              </span>
              {isInstructor ? <Badge variant="accent">讲师</Badge> : null}
              {showRecoveryHint ? (
                <Button variant="outline" size="sm" onClick={() => setRecoveryOpen(true)}>
                  设置找回
                </Button>
              ) : null}
              <Button variant="ghost" size="sm" onClick={logout}>
                退出
              </Button>
            </div>
          ) : (
            <Link href="/login">
              <Button variant="outline" size="sm">
                登录
              </Button>
            </Link>
          )}

          <button
            type="button"
            className="p-2 text-muted-foreground hover:text-warm-text md:hidden"
            onClick={() => setMenuOpen((current) => !current)}
            aria-label="菜单"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              {menuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {menuOpen ? (
        <div className="space-y-2 border-t border-border bg-background px-6 py-3 md:hidden">
          <Link
            href="/"
            className="block py-2 text-sm text-muted-foreground hover:text-warm-text"
            onClick={() => setMenuOpen(false)}
          >
            首页
          </Link>
          {isAuthenticated ? (
            <>
              <Link
                href="/assessment"
                className="block py-2 text-sm text-muted-foreground hover:text-warm-text"
                onClick={() => setMenuOpen(false)}
              >
                主流程工作台
              </Link>
              <Link
                href="/history"
                className="block py-2 text-sm text-muted-foreground hover:text-warm-text"
                onClick={() => setMenuOpen(false)}
              >
                评估历史
              </Link>
              {showRecoveryHint ? (
                <button
                  type="button"
                  className="block py-2 text-sm text-warm-accent hover:underline"
                  onClick={() => {
                    setRecoveryOpen(true);
                    setMenuOpen(false);
                  }}
                >
                  设置找回问题
                </button>
              ) : null}
              <div className="flex items-center justify-between border-t border-border pt-2">
                <span className="text-sm">{user?.display_name || user?.email}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    logout();
                    setMenuOpen(false);
                  }}
                >
                  退出
                </Button>
              </div>
            </>
          ) : (
            <Link
              href="/login"
              className="block py-2 text-sm font-medium text-primary"
              onClick={() => setMenuOpen(false)}
            >
              登录
            </Link>
          )}
        </div>
      ) : null}

      <Dialog open={recoveryOpen} onOpenChange={setRecoveryOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>设置找回问题</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            忘记密码时，可通过安全问题自助找回。请选择问题并设置答案。
          </p>
          <form onSubmit={handleSaveRecovery} className="space-y-4">
            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">找回问题</span>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={recoveryQuestion}
                onChange={(e) => setRecoveryQuestion(e.target.value)}
              >
                {RECOVERY_QUESTIONS.map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm">
              <span className="font-medium">答案</span>
              <Input
                value={recoveryAnswer}
                onChange={(e) => setRecoveryAnswer(e.target.value)}
                placeholder="输入答案"
                required
              />
            </label>
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setRecoveryOpen(false)}>
                取消
              </Button>
              <Button type="submit" loading={recoverySaving}>
                {recoverySaving ? "保存中..." : "保存"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </nav>
  );
}
