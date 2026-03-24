import axios from "axios";
import { TokenPair } from "@/types";

// Логин — POST /api/token/
export async function login(username: string, password: string): Promise<TokenPair> {
  const res = await axios.post<TokenPair>(`${process.env.NEXT_PUBLIC_API_URL}/api/token/`, {
    username,
    password,
  });
  return res.data;
}

// Обновление токена — POST /api/token/refresh/
export async function refreshToken(refresh: string): Promise<{ access: string }> {
  const res = await axios.post<{ access: string }>(
    `${process.env.NEXT_PUBLIC_API_URL}/api/token/refresh/`,
    { refresh }
  );
  return res.data;
}

// Декодирование JWT payload (без верификации — только для UI)
export function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload)) as Record<string, unknown>;
  } catch {
    return {};
  }
}
