import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Low fee credit card network that merchants didn't charg",
  description: "Ferramenta que resolve: low fee credit card network that merchants didn't charge a fee for, so I could c",
  openGraph: {
    title: "Low fee credit card network that merchants didn't charg",
    description: "Ferramenta que resolve: low fee credit card network that merchants didn't charge a fee for, so I could c",
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
