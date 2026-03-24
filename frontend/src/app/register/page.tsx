"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, Trophy } from "lucide-react";
import axios from "axios";

import { register } from "@/services/auth";

type FieldErrors = Partial<Record<string, string>>;

export default function RegisterPage() {
  const router = useRouter();

  const [form, setForm] = useState({
    username:   "",
    first_name: "",
    last_name:  "",
    email:      "",
    city:       "",
    password:   "",
    password2:  "",
  });

  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setFieldErrors({});

    try {
      const res = await register({
        username:   form.username.trim(),
        first_name: form.first_name.trim(),
        last_name:  form.last_name.trim(),
        email:      form.email.trim() || undefined,
        city:       form.city.trim() || undefined,
        password:   form.password,
        password2:  form.password2,
      });

      localStorage.setItem("access_token",  res.access);
      localStorage.setItem("refresh_token", res.refresh);
      localStorage.setItem("user_role",     res.role);
      localStorage.setItem("user_id",       String(res.user_id));
      localStorage.setItem("username",      res.username);

      router.push("/events");
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.data) {
        const data = err.response.data as Record<string, unknown>;
        // Разбираем ошибки по полям
        const fe: FieldErrors = {};
        let hasFieldError = false;
        for (const [key, val] of Object.entries(data)) {
          if (Array.isArray(val)) {
            fe[key] = val.join(" ");
            hasFieldError = true;
          } else if (typeof val === "string") {
            fe[key] = val;
            hasFieldError = true;
          }
        }
        if (hasFieldError) {
          setFieldErrors(fe);
        } else {
          setError("Ошибка при регистрации. Попробуйте ещё раз.");
        }
      } else {
        setError("Ошибка соединения с сервером");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-neutral-50">
      {/* Левая панель */}
      <div className="hidden md:flex w-1/2 bg-linear-to-br from-brand/10 to-brand-light items-center justify-center p-10">
        <div className="text-center">
          <div className="mx-auto mb-6 h-16 w-16 flex items-center justify-center text-brand">
            <Trophy className="h-16 w-16" />
          </div>
          <h1 className="text-3xl font-semibold text-neutral-900">Активный разум</h1>
          <p className="mt-3 text-neutral-600">Платформа рейтинга активности молодёжного парламента</p>
        </div>
      </div>

      {/* Форма */}
      <div className="w-full md:w-1/2 bg-white flex items-center justify-center overflow-y-auto py-10">
        <form onSubmit={handleSubmit} className="max-w-sm w-full mx-auto px-8">
          <h2 className="text-2xl font-semibold text-neutral-900">Регистрация</h2>
          <p className="text-sm text-neutral-500 mt-1 mb-6">Создайте аккаунт участника</p>

          {/* Имя + Фамилия */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-neutral-700 mb-1">
                Имя <span className="text-danger">*</span>
              </label>
              <input
                id="first_name" name="first_name" type="text"
                className={fieldErrors.first_name ? "input border-danger" : "input"}
                value={form.first_name} onChange={handleChange} required
              />
              {fieldErrors.first_name && (
                <p className="text-xs text-danger mt-1">{fieldErrors.first_name}</p>
              )}
            </div>
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-neutral-700 mb-1">
                Фамилия <span className="text-danger">*</span>
              </label>
              <input
                id="last_name" name="last_name" type="text"
                className={fieldErrors.last_name ? "input border-danger" : "input"}
                value={form.last_name} onChange={handleChange} required
              />
              {fieldErrors.last_name && (
                <p className="text-xs text-danger mt-1">{fieldErrors.last_name}</p>
              )}
            </div>
          </div>

          {/* Логин */}
          <div className="mt-4">
            <label htmlFor="username" className="block text-sm font-medium text-neutral-700 mb-1">
              Логин <span className="text-danger">*</span>
            </label>
            <input
              id="username" name="username" type="text"
              className={fieldErrors.username ? "input border-danger" : "input"}
              value={form.username} onChange={handleChange}
              autoComplete="username" required
            />
            {fieldErrors.username && (
              <p className="text-xs text-danger mt-1">{fieldErrors.username}</p>
            )}
          </div>

          {/* Email */}
          <div className="mt-4">
            <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-1">
              Email
            </label>
            <input
              id="email" name="email" type="email"
              className={fieldErrors.email ? "input border-danger" : "input"}
              value={form.email} onChange={handleChange}
              autoComplete="email"
              placeholder="необязательно"
            />
            {fieldErrors.email && (
              <p className="text-xs text-danger mt-1">{fieldErrors.email}</p>
            )}
          </div>

          {/* Город */}
          <div className="mt-4">
            <label htmlFor="city" className="block text-sm font-medium text-neutral-700 mb-1">
              Город
            </label>
            <input
              id="city" name="city" type="text"
              className="input"
              value={form.city} onChange={handleChange}
              placeholder="необязательно"
            />
          </div>

          {/* Пароль */}
          <div className="mt-4">
            <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1">
              Пароль <span className="text-danger">*</span>
            </label>
            <input
              id="password" name="password" type="password"
              className={fieldErrors.password ? "input border-danger" : "input"}
              value={form.password} onChange={handleChange}
              autoComplete="new-password" required
            />
            {fieldErrors.password && (
              <p className="text-xs text-danger mt-1">{fieldErrors.password}</p>
            )}
          </div>

          {/* Подтверждение пароля */}
          <div className="mt-4">
            <label htmlFor="password2" className="block text-sm font-medium text-neutral-700 mb-1">
              Повторите пароль <span className="text-danger">*</span>
            </label>
            <input
              id="password2" name="password2" type="password"
              className={fieldErrors.password2 ? "input border-danger" : "input"}
              value={form.password2} onChange={handleChange}
              autoComplete="new-password" required
            />
            {fieldErrors.password2 && (
              <p className="text-xs text-danger mt-1">{fieldErrors.password2}</p>
            )}
          </div>

          <button
            type="submit"
            className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
            disabled={loading}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            <span>Зарегистрироваться</span>
          </button>

          {error ? (
            <div className="mt-3 p-3 bg-danger/10 text-danger text-sm rounded">{error}</div>
          ) : null}

          <p className="mt-5 text-center text-sm text-neutral-500">
            Уже есть аккаунт?{" "}
            <Link href="/login" className="text-brand font-medium hover:underline">
              Войти
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
