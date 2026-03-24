import { decodeJwtPayload } from "@/services/auth";
import { UserRole } from "@/types";

export function getStoredRole(): UserRole | null {
  if (typeof window === "undefined") return null;

  const storedRole = localStorage.getItem("user_role") as UserRole | null;
  if (storedRole) return storedRole;

  const token = localStorage.getItem("access_token");
  if (!token) return null;

  const payload = decodeJwtPayload(token);
  const tokenRole = payload.role;
  if (
    tokenRole === "ADMIN" ||
    tokenRole === "ORGANIZER" ||
    tokenRole === "PARTICIPANT" ||
    tokenRole === "OBSERVER"
  ) {
    return tokenRole;
  }

  return null;
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("user_id");
  localStorage.removeItem("username");
  window.location.href = "/login";
}
