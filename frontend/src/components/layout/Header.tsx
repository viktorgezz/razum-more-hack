"use client";

import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown, LogOut } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";

import { getStoredRole, logout } from "@/lib/auth";
import { UserRole } from "@/types";

const sectionTitles: Record<string, string> = {
  "/events": "Мероприятия",
  "/leaderboard": "Рейтинг",
  "/organizers": "Организаторы",
  "/my-events": "Мои мероприятия",
  "/inspector": "Кадровый резерв",
  "/admin": "Управление",
  "/profile": "Мой профиль",
};

export default function Header() {
  const pathname = usePathname();
  const [username, setUsername] = useState("User");
  const [role, setRole] = useState<UserRole | null>(null);

  useEffect(() => {
    setUsername(localStorage.getItem("username") || "User");
    setRole(getStoredRole());
  }, []);

  const section = useMemo(() => {
    const key = Object.keys(sectionTitles).find(
      (item) => pathname === item || pathname.startsWith(`${item}/`)
    );
    return key ? sectionTitles[key] : "Панель";
  }, [pathname]);

  const initials = (username || "U").slice(0, 2).toUpperCase();

  return (
    <header className="h-14 bg-white border-b border-neutral-200 px-6 flex items-center justify-between">
      <div className="text-sm font-semibold text-neutral-900">{section}</div>

      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild>
          <button
            type="button"
            className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-neutral-50 transition-colors"
          >
            <div className="h-8 w-8 rounded-full bg-brand text-white text-xs font-semibold flex items-center justify-center">
              {initials}
            </div>
            <div className="text-left leading-tight">
              <p className="text-sm text-neutral-900">{username}</p>
              <p className="text-xs text-neutral-500">{role || "GUEST"}</p>
            </div>
            <ChevronDown className="h-4 w-4 text-neutral-500" />
          </button>
        </DropdownMenu.Trigger>

        <DropdownMenu.Portal>
          <DropdownMenu.Content
            align="end"
            sideOffset={8}
            className="min-w-44 rounded-md border border-neutral-200 bg-white p-1 shadow-card z-50"
          >
            <DropdownMenu.Item
              onSelect={logout}
              className="outline-none rounded-md px-2.5 py-2 text-sm text-neutral-700 hover:bg-neutral-50 cursor-pointer flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Выйти
            </DropdownMenu.Item>
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu.Root>
    </header>
  );
}
