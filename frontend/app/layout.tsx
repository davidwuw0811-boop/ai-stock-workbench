import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI Stock Workbench',
  description: 'AI 选股工作台：多因子选股、情绪分析、强化学习接口、投研报告生成。'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
