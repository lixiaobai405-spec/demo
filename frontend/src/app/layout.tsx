import type { Metadata } from "next";

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
      <body>{children}</body>
    </html>
  );
}
