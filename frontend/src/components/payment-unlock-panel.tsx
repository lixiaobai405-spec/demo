"use client";

import React from "react";
import { useCallback, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { QRCodeSVG } from "qrcode.react";

import { Button } from "@/components/ui/button";
import { getPaymentOrder } from "@/lib/api";
import type {
  AssessmentEntitlementResponse,
  PaymentOrderResponse,
  PaymentProvider,
} from "@/lib/types";
import { useCompleteMockPayment, useCreatePaymentOrder } from "@/hooks/use-payments";
import { assessmentKeys } from "@/hooks/use-assessment";
import { toast } from "@/hooks/use-toast";

const providerLabels: Record<PaymentProvider, string> = {
  wechat: "微信支付",
  alipay: "支付宝",
};

export function PaymentUnlockPanel({
  assessmentId,
  entitlement,
  compact = false,
  onUnlocked,
}: {
  assessmentId: string;
  entitlement: AssessmentEntitlementResponse;
  compact?: boolean;
  onUnlocked?: () => void;
}) {
  const queryClient = useQueryClient();
  const [provider, setProvider] = useState<PaymentProvider>(
    entitlement.latest_order?.provider ?? "wechat",
  );
  const [order, setOrder] = useState<PaymentOrderResponse | null>(
    entitlement.latest_order,
  );
  const [pollError, setPollError] = useState<string | null>(null);
  const createOrder = useCreatePaymentOrder(assessmentId);
  const completeMockPayment = useCompleteMockPayment(assessmentId);

  useEffect(() => {
    if (entitlement.is_unlocked || entitlement.can_continue) {
      onUnlocked?.();
      return;
    }
    if (entitlement.latest_order) {
      setOrder(entitlement.latest_order);
      setProvider(entitlement.latest_order.provider);
    }
  }, [entitlement, onUnlocked]);

  const refreshAssessment = useCallback(async () => {
    await queryClient.invalidateQueries({
      queryKey: assessmentKeys.detail(assessmentId),
    });
    onUnlocked?.();
  }, [assessmentId, onUnlocked, queryClient]);

  useEffect(() => {
    if (!order || order.status !== "pending") return;

    const intervalId = window.setInterval(async () => {
      try {
        const latest = await getPaymentOrder(order.order_id);
        setOrder(latest);
        setPollError(null);
        if (latest.status === "paid") {
          toast({
            title: "支付成功",
            description: "当前评估已解锁，后续 AI 创新方案可以继续生成。",
          });
          await refreshAssessment();
        }
      } catch (error) {
        setPollError(error instanceof Error ? error.message : "订单状态查询失败");
      }
    }, 2500);

    return () => window.clearInterval(intervalId);
  }, [order, refreshAssessment]);

  const handleCreateOrder = useCallback(async () => {
    try {
      const nextOrder = await createOrder.mutateAsync(provider);
      setOrder(nextOrder);
      setPollError(null);
      toast({
        title: "支付订单已创建",
        description: `请使用${providerLabels[nextOrder.provider]}扫码完成解锁。`,
      });
    } catch (error) {
      toast({
        title: "创建支付订单失败",
        description:
          error instanceof Error ? error.message : "请稍后重试或联系管理员。",
        variant: "destructive",
      });
    }
  }, [createOrder, provider]);

  const handleMockComplete = useCallback(async () => {
    if (!order) return;
    try {
      await completeMockPayment.mutateAsync(order);
      const latest = await getPaymentOrder(order.order_id);
      setOrder(latest);
      if (latest.status === "paid") {
        toast({
          title: "mock 支付成功",
          description: "已通过本地 mock 回调解锁当前评估。",
        });
        await refreshAssessment();
      }
    } catch (error) {
      toast({
        title: "mock 支付失败",
        description:
          error instanceof Error ? error.message : "请检查后端 mock 支付配置。",
        variant: "destructive",
      });
    }
  }, [completeMockPayment, order, refreshAssessment]);

  const activeOrder = order ?? entitlement.latest_order;
  const isMockOrder = Boolean(activeOrder?.qr_code_url?.startsWith("mockpay://"));
  const amountLabel = activeOrder
    ? formatAmount(activeOrder.amount_cents, activeOrder.currency)
    : "以订单为准";

  return (
    <section
      className={
        compact
          ? "space-y-5"
          : "rounded-2xl border border-amber-200 bg-amber-50/60 p-6"
      }
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">付费解锁</p>
          <h2 className={compact ? "text-xl font-semibold" : "section-heading"}>
            解锁完整 AI 创新方案
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-muted-foreground">
            问卷、企业画像和商业画布诊断免费。支付后仅解锁当前评估的突破要素、创新方向、AI 场景、竞争力、终局、报告和导出。
          </p>
        </div>
        <span className="badge badge-warning">当前评估 {amountLabel}</span>
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-xl border border-warm-border-light bg-warm-surface p-4">
          <p className="text-sm font-medium text-warm-text">支付方式</p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {(["wechat", "alipay"] as PaymentProvider[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setProvider(item)}
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                  provider === item
                    ? "border-warm-accent bg-warm-accent text-white"
                    : "border-warm-border-light bg-warm-inset text-warm-text hover:border-warm-accent"
                }`}
              >
                {providerLabels[item]}
              </button>
            ))}
          </div>
          <Button
            type="button"
            className="mt-4 w-full"
            onClick={handleCreateOrder}
            loading={createOrder.isPending}
            disabled={createOrder.isPending}
          >
            {activeOrder?.status === "pending" ? "刷新支付二维码" : "创建扫码订单"}
          </Button>
        </div>

        <div className="rounded-xl border border-warm-border-light bg-warm-surface p-4">
          {activeOrder?.qr_code_url ? (
            <div className="grid gap-4 sm:grid-cols-[180px_1fr]">
              <div className="flex aspect-square items-center justify-center rounded-xl border border-warm-border-light bg-white p-3">
                <QRCodeSVG
                  value={activeOrder.qr_code_url}
                  size={156}
                  marginSize={2}
                />
              </div>
              <div className="text-sm leading-7 text-muted-foreground">
                <p className="font-medium text-warm-text">
                  {providerLabels[activeOrder.provider]}订单
                </p>
                <p>订单状态：{formatOrderStatus(activeOrder.status)}</p>
                <p>过期时间：{formatDateTime(activeOrder.expires_at)}</p>
                <p className="break-all font-mono text-xs">
                  {activeOrder.qr_code_url}
                </p>
                {isMockOrder ? (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-3"
                    onClick={handleMockComplete}
                    loading={completeMockPayment.isPending}
                    disabled={completeMockPayment.isPending}
                  >
                    模拟支付成功
                  </Button>
                ) : null}
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-warm-border-light bg-warm-inset p-6 text-sm leading-7 text-muted-foreground">
              选择支付方式后创建订单，这里会展示用于扫码支付的二维码。支付成功后页面会自动刷新解锁状态。
            </div>
          )}

          {pollError ? (
            <p className="mt-3 text-sm text-destructive">{pollError}</p>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function formatAmount(amountCents: number, currency: string): string {
  const amount = amountCents / 100;
  if (currency === "CNY") return `￥${amount.toFixed(2)}`;
  return `${amount.toFixed(2)} ${currency}`;
}

function formatOrderStatus(status: PaymentOrderResponse["status"]): string {
  const labels: Record<PaymentOrderResponse["status"], string> = {
    pending: "待支付",
    paid: "已支付",
    failed: "支付失败",
    expired: "已过期",
    canceled: "已取消",
  };
  return labels[status];
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}
