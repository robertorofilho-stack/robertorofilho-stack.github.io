import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "{{NOME}}",
  description: "{{DESCRICAO}}",
  openGraph: {
    title: "{{NOME}}",
    description: "{{DESCRICAO}}",
    type: "website",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="min-h-full antialiased">{children}</body>
    </html>
  );
}
