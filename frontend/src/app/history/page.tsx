"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { AuthGuard } from "@/components/auth-guard";
import { AssessmentCard } from "@/components/assessment-card";
import {
  HistoryFilterBar,
  type HistoryFilters,
} from "@/components/history-filter-bar";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { deleteAssessment, listMyAssessments } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

function HistoryContent() {
  const [filters, setFilters] = useState<HistoryFilters>({
    search: "",
    dateFrom: "",
    dateTo: "",
    industry: "",
  });
  const [page, setPage] = useState(1);
  const [deleteMode, setDeleteMode] = useState(false);

  const handleDelete = async (id: string) => {
    if (!window.confirm("确认删除这条评估记录吗？删除后将无法恢复。")) return;
    try {
      await deleteAssessment(id);
      toast({ title: "已删除", variant: "success" });
      refetch();
    } catch (error) {
      toast({
        title: "删除失败",
        description: error instanceof Error ? error.message : "请稍后重试",
        variant: "destructive",
      });
    }
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["my-assessments", filters, page],
    queryFn: () =>
      listMyAssessments({
        search: filters.search || undefined,
        date_from: filters.dateFrom || undefined,
        date_to: filters.dateTo || undefined,
        industry: filters.industry || undefined,
        page,
        page_size: 20,
      }),
  });

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <section className="mb-8">
          <Link
            href="/"
            className="text-xs text-muted-foreground hover:text-warm-text transition-colors"
          >
            ← 返回首页
          </Link>
          <h1 className="mt-3 font-heading text-3xl font-bold text-warm-text">
            评估历史
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            浏览和管理你的所有企业评估记录
          </p>
        </section>

        {/* Filters */}
        <HistoryFilterBar
          filters={filters}
          onChange={(f) => { setFilters(f); setPage(1); }}
          deleteMode={deleteMode}
          onToggleDeleteMode={() => setDeleteMode((d) => !d)}
        />

        {/* Content */}
        <section className="mt-6">
          {isLoading ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card space-y-3">
                  <Skeleton className="h-6 w-40 rounded-xl" />
                  <Skeleton className="h-4 w-24 rounded-xl" />
                  <Skeleton className="h-4 w-32 rounded-xl" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="card-inset text-center py-12">
              <p className="text-muted-foreground">加载失败</p>
              <Button variant="outline" size="sm" onClick={() => refetch()} className="mt-3">
                重试
              </Button>
            </div>
          ) : data && data.total > 0 ? (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                {data.items.map((item) => (
                  <AssessmentCard
                    key={item.id}
                    item={item}
                    deleteMode={deleteMode}
                    onDelete={handleDelete}
                  />
                ))}
              </div>

              {/* Pagination */}
              {data.total_pages > 1 && (
                <div className="mt-6 flex items-center justify-center gap-3">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    上一页
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {page} / {data.total_pages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= data.total_pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    下一页
                  </Button>
                </div>
              )}
            </>
          ) : (
            <div className="card-inset text-center py-16">
              <p className="text-lg font-medium text-warm-text">尚无评估记录</p>
              <p className="mt-2 text-sm text-muted-foreground">
                创建你的第一份企业 AI 创新评估
              </p>
              <Link href="/assessment" className="inline-block mt-4">
                <Button>开始企业问卷</Button>
              </Link>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default function HistoryPage() {
  return (
    <AuthGuard>
      <HistoryContent />
    </AuthGuard>
  );
}
