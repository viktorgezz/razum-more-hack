import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Активный разум",
  description: "Платформа рейтинга активности молодёжного парламента",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
