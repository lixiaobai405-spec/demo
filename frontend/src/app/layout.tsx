import type { Metadata } from "next";

import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "@/components/ui/toaster";

import "./globals.css";

export const metadata: Metadata = {
  title: "美太 AI 商业创新智能体 Demo",
  description: "企业问卷与企业画像 Demo，验证前后端基础咨询链路。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&family=JetBrains+Mono:wght@400;500&family=Lora:ital,wght@0,400..600;0,700;1,400..600&family=Noto+Sans+SC:wght@300..700&family=Noto+Serif+SC:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400..700;1,400..700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <QueryProvider>
          {children}
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
