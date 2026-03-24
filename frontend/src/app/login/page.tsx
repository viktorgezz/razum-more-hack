"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Trophy } from "lucide-react";
import axios from "axios";

import { decodeJwtPayload, login } from "@/services/auth";

type JwtPayload = {
  role?: string;
  user_id?: number | string;
  username?: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const tokens = await login(username, password);
      localStorage.setItem("access_token", tokens.access);
      localStorage.setItem("refresh_token", tokens.refresh);

      const payload = decodeJwtPayload(tokens.access) as JwtPayload;
      const role = payload.role ?? "";
      const userId = payload.user_id?.toString() ?? "";
      const payloadUsername = payload.username ?? username;

      localStorage.setItem("user_role", role);
      localStorage.setItem("user_id", userId);
      localStorage.setItem("username", payloadUsername);

      router.push("/events");
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        setError("Неверный логин или пароль");
      } else {
        setError("Ошибка соединения с сервером");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-neutral-50">
      <div className="hidden md:flex w-1/2 bg-linear-to-br from-brand/10 to-brand-light items-center justify-center p-10">
        <div className="text-center">
          <div className="mx-auto mb-6 h-16 w-16 flex items-center justify-center text-brand">
            <Trophy className="h-16 w-16" />
          </div>
          <h1 className="text-3xl font-semibold text-neutral-900">Платформа рейтинга активности</h1>
          <p className="mt-3 text-neutral-600">Молодёжный парламент и кадровый резерв</p>
        </div>
      </div>

      <div className="w-full md:w-1/2 bg-white flex items-center justify-center">
        <form onSubmit={handleSubmit} className="max-w-sm w-full mx-auto px-8">
          <h2 className="text-2xl font-semibold text-neutral-900">Войти</h2>
          <p className="text-sm text-neutral-500 mt-1 mb-6">Введите логин и пароль</p>

          <label htmlFor="username" className="block text-sm font-medium text-neutral-700 mb-1">
            Логин
          </label>
          <input
            id="username"
            name="username"
            type="text"
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />

          <div className="mt-4">
            <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1">
              Пароль
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <button type="submit" className="btn-primary w-full mt-6 flex items-center justify-center gap-2" disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            <span>Войти</span>
          </button>

          {error ? <div className="mt-3 p-3 bg-danger/10 text-danger text-sm rounded">{error}</div> : null}
        </form>
      </div>
    </div>
  );
}
