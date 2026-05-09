"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "@/hooks/use-toast";

const DRAFT_PREFIX = "draft:";
const DEBOUNCE_MS = 2000;

/**
 * Auto-saves form values to localStorage with debounce.
 * Restores draft on mount (with toast notification).
 */
export function useFormAutosave<T extends Record<string, unknown>>(
  key: string,
  formValues: T,
  enabled: boolean = true,
) {
  const storageKey = `${DRAFT_PREFIX}${key}`;
  const [isRestored, setIsRestored] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Restore draft on mount
  useEffect(() => {
    if (!enabled) return;
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      return; // Don't auto-restore — let caller decide
    } catch {
      // localStorage not available
    }
  }, [storageKey, enabled]);

  // Check if draft exists (for caller to show restore prompt)
  const hasDraft = useCallback((): boolean => {
    try {
      return localStorage.getItem(storageKey) !== null;
    } catch {
      return false;
    }
  }, [storageKey]);

  // Read draft
  const readDraft = useCallback((): T | null => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      const parsed = JSON.parse(raw) as T;
      setIsRestored(true);
      toast({
        title: "已恢复草稿",
        description: "上次未提交的内容已自动恢复。",
      });
      return parsed;
    } catch {
      return null;
    }
  }, [storageKey]);

  // Auto-save with debounce
  useEffect(() => {
    if (!enabled || !isRestored && !hasDraft()) {
      // No values to save on first render before user types
    }
    if (!enabled) return;

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(() => {
      try {
        const json = JSON.stringify(formValues);
        if (json.length < 4) return; // Empty or trivial
        localStorage.setItem(storageKey, json);
      } catch {
        // localStorage full or not available
      }
    }, DEBOUNCE_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [formValues, storageKey, enabled]);

  // Clear draft
  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(storageKey);
    } catch {
      // ignore
    }
  }, [storageKey]);

  return { hasDraft, readDraft, clearDraft, isRestored };
}
