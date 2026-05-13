"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import { getConversation, clearConversation } from "@/lib/api";
import type { ChatMessageOut } from "@/lib/types";
import { Button } from "@/components/ui/button";

function extractAssessmentId(pathname: string): string | null {
  const match = pathname.match(/\/assessment\/([a-zA-Z0-9_-]+)/);
  return match ? match[1] : null;
}

export function AIChatPanel() {
  const pathname = usePathname();
  const assessmentId = extractAssessmentId(pathname);
  const queryClient = useQueryClient();

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState("");
  const [error, setError] = useState<string | null>(null);

  // FAB drag state
  const [fabPos, setFabPos] = useState({ x: 24, y: 24 });
  const dragRef = useRef({
    dragging: false,
    startX: 0,
    startY: 0,
    startFabX: 24,
    startFabY: 24,
    moved: false,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // FAB drag handlers
  const onFabPointerDown = useCallback((e: React.PointerEvent) => {
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    dragRef.current = {
      dragging: true,
      startX: e.clientX,
      startY: e.clientY,
      startFabX: fabPos.x,
      startFabY: fabPos.y,
      moved: false,
    };
  }, [fabPos]);

  const onFabPointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragRef.current.dragging) return;
    const dx = dragRef.current.startX - e.clientX;
    const dy = dragRef.current.startY - e.clientY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      dragRef.current.moved = true;
    }
    setFabPos({
      x: dragRef.current.startFabX + dx,
      y: dragRef.current.startFabY + dy,
    });
  }, []);

  const onFabPointerUp = useCallback((e: React.PointerEvent) => {
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    dragRef.current.dragging = false;
    if (!dragRef.current.moved) {
      setOpen((v) => !v);
    }
  }, []);

  const convQuery = useQuery({
    queryKey: ["chat", assessmentId],
    queryFn: ({ signal }) => getConversation(assessmentId!, { signal }),
    enabled: Boolean(assessmentId) && open,
    staleTime: 0,
  });

  const messages = convQuery.data?.messages ?? [];

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamText]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  // Cross-tab context sync
  useEffect(() => {
    if (!assessmentId) return;
    const channel = new BroadcastChannel("ai-chat-context");
    channel.onmessage = (event) => {
      if (
        event.data?.type === "context-updated" &&
        event.data?.assessmentId === assessmentId
      ) {
        queryClient.invalidateQueries({ queryKey: ["chat", assessmentId] });
      }
    };
    return () => channel.close();
  }, [assessmentId, queryClient]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || !assessmentId || streaming) return;

    setInput("");
    setError(null);
    setStreaming(true);
    setStreamText("");

    abortRef.current = new AbortController();

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
      const response = await fetch(
        `${apiBase}/api/assessments/${assessmentId}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
          signal: abortRef.current.signal,
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              setStreamText((prev) => prev + data.token);
            }
            if (data.error) {
              setError(data.error);
            }
            if (data.done) {
              setStreamText("");
              queryClient.invalidateQueries({
                queryKey: ["chat", assessmentId],
              });
            }
          } catch {
            // skip unparseable lines
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "发送失败");
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [input, assessmentId, streaming, queryClient]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage],
  );

  const handleClear = useCallback(async () => {
    if (!assessmentId) return;
    await clearConversation(assessmentId);
    queryClient.invalidateQueries({ queryKey: ["chat", assessmentId] });
  }, [assessmentId, queryClient]);

  // Don't render on non-assessment pages
  if (!assessmentId) return null;

  return (
    <>
      {/* FAB Button — draggable */}
      <button
        type="button"
        onPointerDown={onFabPointerDown}
        onPointerMove={onFabPointerMove}
        onPointerUp={onFabPointerUp}
        className="fixed z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-shadow duration-200 hover:shadow-xl touch-none select-none cursor-grab active:cursor-grabbing"
        style={{ right: fabPos.x, bottom: fabPos.y }}
        aria-label="AI 商业顾问"
      >
        {open ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        )}
      </button>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm transition-opacity"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Slide-out Drawer */}
      <div
        className={`fixed right-0 top-0 z-40 flex h-full w-full max-w-md flex-col border-l border-border bg-background shadow-2xl transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-warm-text">AI 商业顾问</p>
            <p className="text-[11px] text-warm-muted">基于当前评估数据回答</p>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={handleClear}
              className="rounded-md px-2 py-1 text-xs text-warm-muted hover:bg-secondary"
              title="清空对话"
            >
              清空
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="ml-1 rounded-md p-1.5 text-warm-muted hover:bg-secondary"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {convQuery.isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : messages.length === 0 && !streaming ? (
            <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
              <div className="mb-3 text-3xl">💬</div>
              <p className="text-sm font-medium text-warm-text">AI 商业创新顾问</p>
              <p className="mt-2 text-xs leading-5 text-warm-muted">
                我可以基于当前企业的评估数据（画像、画布、方向延展、终局设计等），
                回答你的商业创新问题。随着你生成更多评估结果，我的知识也会更新。
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}

              {/* Streaming message */}
              {streaming && streamText && (
                <MessageBubble
                  message={{
                    id: "streaming",
                    role: "assistant",
                    content: streamText,
                    created_at: null,
                  }}
                  isStreaming
                />
              )}

              {streaming && !streamText && (
                <div className="flex items-center gap-2 py-2">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:0ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:300ms]" />
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">
                  {error}
                  <button
                    type="button"
                    onClick={() => setError(null)}
                    className="ml-2 underline"
                  >
                    关闭
                  </button>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border px-4 py-3">
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入问题..."
              rows={2}
              disabled={streaming}
              className="flex-1 resize-none rounded-xl border border-border bg-secondary/50 px-3 py-2 text-sm text-warm-text placeholder:text-warm-muted focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
            />
            {streaming ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => abortRef.current?.abort()}
              >
                停止
              </Button>
            ) : (
              <Button
                type="button"
                size="sm"
                onClick={sendMessage}
                disabled={!input.trim()}
              >
                发送
              </Button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

function MessageBubble({
  message,
  isStreaming,
}: {
  message: ChatMessageOut;
  isStreaming?: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-6 ${
          isUser
            ? "bg-primary text-primary-foreground rounded-br-md"
            : "bg-secondary text-warm-text rounded-bl-md"
        } ${isStreaming ? "animate-pulse" : ""}`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {isStreaming && (
          <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-current align-text-bottom" />
        )}
      </div>
    </div>
  );
}
