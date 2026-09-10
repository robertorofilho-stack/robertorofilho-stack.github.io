import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Convert bank CSV export into a clean monthly spending s",
  description: "Ferramenta que resolve: convert bank CSV export into a clean monthly spending summary",
  openGraph: {
    title: "Convert bank CSV export into a clean monthly spending s",
    description: "Ferramenta que resolve: convert bank CSV export into a clean monthly spending summary",
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
