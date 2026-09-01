import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/components/Providers';

export const metadata: Metadata = {
  title: 'Autonomous AI Data Analyst | Enterprise SaaS Platform',
  description: 'Production-grade enterprise AI data analysis platform built with Next.js 15, FastAPI, Firebase, and AWS.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
