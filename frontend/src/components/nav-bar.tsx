"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/providers/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function NavBar() {
  const { isAuthenticated, user, isInstructor, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        {/* Left: logo + links */}
        <div className="flex items-center gap-6">
          <Link href="/" className="font-heading text-lg font-bold text-warm-text hover:text-primary transition-colors">
            美太 AI
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link href="/" className="text-sm text-muted-foreground hover:text-warm-text transition-colors">
              首页
            </Link>
            {isAuthenticated && (
              <>
                <Link href="/history" className="text-sm text-muted-foreground hover:text-warm-text transition-colors">
                  评估历史
                </Link>
                <Link href="/intake" className="text-sm text-muted-foreground hover:text-warm-text transition-colors">
                  导入材料
                </Link>
                <Link href="/assessment" className="text-sm text-muted-foreground hover:text-warm-text transition-colors">
                  企业问卷
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Right: user menu */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-3">
              <span className="text-sm text-warm-text">
                {user?.display_name || user?.email}
              </span>
              {isInstructor && (
                <Badge variant="accent">讲师</Badge>
              )}
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

          {/* Mobile menu toggle */}
          <button
            type="button"
            className="md:hidden p-2 text-muted-foreground hover:text-warm-text"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="菜单"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-border bg-background px-6 py-3 space-y-2">
          <Link href="/" className="block text-sm text-muted-foreground hover:text-warm-text py-2" onClick={() => setMenuOpen(false)}>首页</Link>
          {isAuthenticated && (
            <>
              <Link href="/history" className="block text-sm text-muted-foreground hover:text-warm-text py-2" onClick={() => setMenuOpen(false)}>评估历史</Link>
              <Link href="/intake" className="block text-sm text-muted-foreground hover:text-warm-text py-2" onClick={() => setMenuOpen(false)}>导入材料</Link>
              <Link href="/assessment" className="block text-sm text-muted-foreground hover:text-warm-text py-2" onClick={() => setMenuOpen(false)}>企业问卷</Link>
              <div className="pt-2 border-t border-border flex items-center justify-between">
                <span className="text-sm">{user?.display_name || user?.email}</span>
                <Button variant="ghost" size="sm" onClick={() => { logout(); setMenuOpen(false); }}>退出</Button>
              </div>
            </>
          )}
          {!isAuthenticated && (
            <Link href="/login" className="block text-sm text-primary font-medium py-2" onClick={() => setMenuOpen(false)}>登录</Link>
          )}
        </div>
      )}
    </nav>
  );
}
