"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, Calendar, ClipboardList, LogOut, Settings, Trophy, User, Users } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { cn } from "@/lib/utils";
import { getStoredRole, logout } from "@/lib/auth";
import { UserRole } from "@/types";

type MenuItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  hidden?: (role: UserRole | null) => boolean;
};

const menuItems: MenuItem[] = [
  { label: "Мероприятия", href: "/events", icon: Calendar },
  { label: "Рейтинг", href: "/leaderboard", icon: Trophy },
  { label: "Организаторы", href: "/organizers", icon: Users },
  {
    label: "Мои мероприятия",
    href: "/my-events",
    icon: ClipboardList,
    hidden: (role) => role !== "ORGANIZER" && role !== "ADMIN",
  },
  {
    label: "Кадровый резерв",
    href: "/inspector",
    icon: Briefcase,
    hidden: (role) => role === "PARTICIPANT" || role === "ORGANIZER",
  },
  {
    label: "Управление",
    href: "/admin",
    icon: Settings,
    hidden: (role) => role !== "ADMIN",
  },
  { label: "Мой профиль", href: "/profile", icon: User },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [role, setRole] = useState<UserRole | null>(null);
  const [username, setUsername] = useState("");

  useEffect(() => {
    setRole(getStoredRole());
    setUsername(localStorage.getItem("username") || "User");
  }, []);

  const visibleItems = useMemo(
    () => menuItems.filter((item) => (item.hidden ? !item.hidden(role) : true)),
    [role]
  );

  const initials = (username || "U").slice(0, 2).toUpperCase();

  return (
    <aside className="w-60 bg-white border-r border-neutral-200 h-screen flex flex-col">
      <div className="p-4 border-b border-neutral-200">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-full bg-brand text-white flex items-center justify-center">
            <Trophy className="h-4 w-4" />
          </div>
          <span className="font-semibold text-neutral-900">Парламент</span>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "rounded-md px-3 py-2 flex items-center gap-2.5 text-sm transition-colors cursor-pointer",
                active
                  ? "bg-neutral-100 text-neutral-900 font-medium"
                  : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-800"
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-neutral-200">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="h-8 w-8 rounded-full bg-brand text-white text-xs font-semibold flex items-center justify-center shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-neutral-900 truncate">{username}</p>
              <p className="text-xs text-neutral-500">{role || "GUEST"}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={logout}
            className="p-2 rounded-md text-neutral-500 hover:bg-neutral-100 hover:text-neutral-800 transition-colors"
            aria-label="Выйти"
            title="Выйти"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
