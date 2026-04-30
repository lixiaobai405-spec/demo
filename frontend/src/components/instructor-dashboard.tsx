"use client";

import { useEffect, useState } from "react";
import type { InstructorDashboardResponse, StudentSummary } from "@/lib/types";
import { getInstructorDashboard, batchComment, instructorExportCsv } from "@/lib/api";

const progressIcon = (flag: boolean) => (flag ? "✅" : "⬜");

export function InstructorDashboard() {
  const [data, setData] = useState<InstructorDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [commentDraft, setCommentDraft] = useState("");
  const [commentStatus, setCommentStatus] = useState<string | null>(null);

  const [groupFilter, setGroupFilter] = useState<string>("全部");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    try {
      const result = await getInstructorDashboard();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载讲师仪表盘失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleBatchComment() {
    if (!commentDraft.trim() || selectedIds.size === 0) return;
    try {
      const result = await batchComment({
        assessment_ids: Array.from(selectedIds),
        comment: commentDraft,
      });
      setCommentStatus(`已点评 ${result.updated_count} 名学员。`);
      setCommentDraft("");
      loadDashboard();
    } catch {
      setCommentStatus("点评提交失败，请重试。");
    }
  }

  async function handleExport() {
    try {
      const result = await instructorExportCsv();
      const blob = new Blob([result.content], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `instructor_export_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("导出失败");
    }
  }

  function toggleSelect(id: string) {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  }

  function toggleSelectAll(students: StudentSummary[]) {
    if (selectedIds.size === students.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(students.map((s) => s.assessment_id)));
    }
  }

  if (loading) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-slate-400">
        正在加载讲师仪表盘...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-rose-300">
        {error || "暂无数据"}
      </div>
    );
  }

  const filtered =
    groupFilter === "全部"
      ? data.students
      : data.students.filter((s) => (s.class_group || "未分组") === groupFilter);

  const allFilteredIds = filtered.map((s) => s.assessment_id);

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-slate-400">
            Instructor Dashboard
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            讲师工作台
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] uppercase text-slate-500">学员数</p>
            <p className="text-xl font-bold text-white">{data.total_students}</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase text-slate-500">报告完成率</p>
            <p className="text-xl font-bold text-emerald-300">
              {data.overall_completion_pct}%
            </p>
          </div>
          <button
            type="button"
            onClick={handleExport}
            className="rounded-full bg-white/10 px-4 py-2 text-sm text-white hover:bg-white/20"
          >
            导出 CSV
          </button>
        </div>
      </div>

      {/* Group summary */}
      {data.groups.length > 1 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {["全部", ...data.groups].map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => setGroupFilter(g)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                groupFilter === g
                  ? "bg-indigo-300/20 text-indigo-100 border border-indigo-300/30"
                  : "border border-white/10 text-slate-400 hover:text-white"
              }`}
            >
              {g}
              {g !== "全部" && data.summary_by_group[g] != null && (
                <span className="ml-1 text-slate-500">({data.summary_by_group[g]})</span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Batch comment bar */}
      <div className="mt-4 flex flex-wrap items-center gap-3 rounded-2xl border border-white/8 bg-slate-950/50 p-3">
        <input
          className="min-w-[240px] flex-1 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500"
          placeholder={`批量点评（已选 ${selectedIds.size} 人）...`}
          value={commentDraft}
          onChange={(e) => setCommentDraft(e.target.value)}
        />
        <button
          type="button"
          onClick={handleBatchComment}
          disabled={selectedIds.size === 0 || !commentDraft.trim()}
          className="flex-shrink-0 rounded-full bg-indigo-400 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-300 disabled:opacity-40"
        >
          提交点评
        </button>
        {commentStatus && (
          <span className="text-xs text-emerald-300">{commentStatus}</span>
        )}
      </div>

      {/* Student table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-white/8">
              <th className="pb-2 pr-2">
                <input
                  type="checkbox"
                  checked={selectedIds.size === filtered.length && filtered.length > 0}
                  onChange={() => toggleSelectAll(filtered)}
                  className="rounded"
                />
              </th>
              <th className="pb-2 pr-3 font-medium text-slate-400">企业</th>
              <th className="pb-2 px-2 font-medium text-slate-400 hidden sm:table-cell">行业</th>
              <th className="pb-2 px-2 font-medium text-slate-400 hidden md:table-cell">分组</th>
              <th className="pb-2 px-1 text-center font-medium text-slate-400">P</th>
              <th className="pb-2 px-1 text-center font-medium text-slate-400">C</th>
              <th className="pb-2 px-1 text-center font-medium text-slate-400">B</th>
              <th className="pb-2 px-1 text-center font-medium text-slate-400">S</th>
              <th className="pb-2 px-1 text-center font-medium text-slate-400">R</th>
              <th className="pb-2 px-2 font-medium text-slate-400 hidden lg:table-cell">讲师备注</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((student) => (
              <tr
                key={student.assessment_id}
                className="border-b border-white/5 hover:bg-white/5"
              >
                <td className="py-2 pr-2">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(student.assessment_id)}
                    onChange={() => toggleSelect(student.assessment_id)}
                    className="rounded"
                  />
                </td>
                <td className="py-2 pr-3">
                  <p className="font-medium text-white truncate max-w-[140px]">
                    {student.company_name}
                  </p>
                </td>
                <td className="py-2 px-2 hidden sm:table-cell">
                  <span className="text-slate-400">{student.industry}</span>
                </td>
                <td className="py-2 px-2 hidden md:table-cell">
                  <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-slate-300">
                    {student.class_group || "未分组"}
                  </span>
                </td>
                <td className="py-2 px-1 text-center text-[10px]">
                  {progressIcon(student.has_profile)}
                </td>
                <td className="py-2 px-1 text-center text-[10px]">
                  {progressIcon(student.has_canvas)}
                </td>
                <td className="py-2 px-1 text-center text-[10px]">
                  {progressIcon(student.has_breakthrough)}
                </td>
                <td className="py-2 px-1 text-center text-[10px]">
                  {progressIcon(student.has_scenarios)}
                </td>
                <td className="py-2 px-1 text-center text-[10px]">
                  {student.has_report ? "📄" : "⬜"}
                </td>
                <td className="py-2 px-2 hidden lg:table-cell">
                  <p className="text-[10px] text-slate-500 max-w-[180px] truncate">
                    {student.instructor_comment || "—"}
                  </p>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={10} className="py-6 text-center text-slate-500">
                  暂无所选分组的学员数据
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
