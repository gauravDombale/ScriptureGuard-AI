import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ScriptureGuard AI",
  description: "Grounded Christianity assistant with verified KJV citations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
