"use client";

import { Badge } from "@/components/ui/badge";
import type { CompanyProfileResult } from "@/lib/types";

export function ProfileResultsSection({
  companyProfile,
  profileMode,
}: {
  companyProfile: CompanyProfileResult;
  profileMode: "mock" | "live" | null;
}) {
  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">画像结果</p>
          <h2 className="section-heading">企业画像结果</h2>
        </div>
        {companyProfile ? (
          <Badge variant={profileMode === "live" ? "success" : "accent"}>
            {profileMode === "mock" ? "模拟" : "真实"}
          </Badge>
        ) : null}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <ProfileBlock title="企业概览" content={companyProfile.company_summary} />
        <ProfileBlock title="价值主张" content={companyProfile.value_proposition} />
        <ProfileBlock title="客户与市场" content={companyProfile.customer_and_market} />
        <ProfileBlock title="运营与资源基础" content={companyProfile.operations_and_resources} />
        <ProfileBlock title="数字化与 AI 准备度" content={companyProfile.digital_and_ai_readiness} />
        <ListBlock title="关键挑战" items={companyProfile.key_challenges} />
        <ListBlock title="优先 AI 切入方向" items={companyProfile.priority_ai_directions} />
        <ListBlock title="待补充信息" items={companyProfile.missing_information} />
      </div>
    </div>
  );
}

function ProfileBlock({ title, content }: { title: string; content: string }) {
  return (
    <div className="rounded-xl border border-border bg-secondary p-6">
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
        {title}
      </p>
      <p className="mt-3 text-sm leading-7">{content}</p>
    </div>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl border border-border bg-secondary p-6">
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
        {title}
      </p>
      <ul className="mt-3 space-y-2">
        {items.map((item, i) => (
          <li
            key={`${title}-${i}`}
            className="rounded-xl bg-card px-4 py-3 text-sm"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
