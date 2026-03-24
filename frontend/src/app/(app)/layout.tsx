"use client";

import { useEffect } from "react";
import type { ReactNode } from "react";
import { useRouter } from "next/navigation";

import AppLayout from "@/components/layout/AppLayout";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      router.push("/login");
    }
  }, [router]);

  return <AppLayout>{children}</AppLayout>;
}
