import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Suki PromiseGuard",
  description: "Evidence-backed customer recovery operations for Suki Mart",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
