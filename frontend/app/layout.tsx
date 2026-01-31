import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PartSelect Assistant",
  description: "Chat assistant for refrigerator and dishwasher parts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
