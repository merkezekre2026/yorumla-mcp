import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Yorumla MCP",
  description: "Hepsiburada yorumları için AI satın alma karar motoru"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
