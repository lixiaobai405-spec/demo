"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export type HistoryFilters = {
  search: string;
  dateFrom: string;
  dateTo: string;
  industry: string;
};

export function HistoryFilterBar({
  filters,
  onChange,
}: {
  filters: HistoryFilters;
  onChange: (f: HistoryFilters) => void;
}) {
  const [local, setLocal] = useState(filters);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => onChange(local), 300);
    return () => clearTimeout(timer);
  }, [local.search]);

  function applyDateRange() {
    onChange(local);
  }

  function reset() {
    const empty = { search: "", dateFrom: "", dateTo: "", industry: "" };
    setLocal(empty);
    onChange(empty);
  }

  const hasFilters = filters.search || filters.dateFrom || filters.dateTo || filters.industry;

  return (
    <div className="card space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Input
          value={local.search}
          onChange={(e) => setLocal((p) => ({ ...p, search: e.target.value }))}
          placeholder="搜索公司名称..."
        />
        <Input
          type="date"
          value={local.dateFrom}
          onChange={(e) => setLocal((p) => ({ ...p, dateFrom: e.target.value }))}
          placeholder="开始日期"
        />
        <Input
          type="date"
          value={local.dateTo}
          onChange={(e) => setLocal((p) => ({ ...p, dateTo: e.target.value }))}
          placeholder="结束日期"
        />
        <Input
          value={local.industry}
          onChange={(e) => setLocal((p) => ({ ...p, industry: e.target.value }))}
          placeholder="行业筛选..."
        />
      </div>
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={applyDateRange}>
          应用日期筛选
        </Button>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={reset}>
            清除所有筛选
          </Button>
        )}
      </div>
    </div>
  );
}
