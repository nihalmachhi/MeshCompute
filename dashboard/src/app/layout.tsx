import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "MeshCompute | Operations", description: "Distributed work queue operations dashboard" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
