"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Calendar, MapPin, Search, Star, TrendingUp } from "lucide-react";

import { getOrganizers } from "@/services/organizers";
import { OrganizerList } from "@/types";
import { cn } from "@/lib/utils";

type OrganizerListWithTrust = OrganizerList & {
  avg_trust_score?: string | number | null;
};

function OrganizerCard({ organizer }: { organizer: OrganizerListWithTrust }) {
  const router = useRouter();
  const fullName = `${organizer.first_name} ${organizer.last_name}`.trim() || "Без имени";
  const initials = `${organizer.first_name?.[0] || ""}${organizer.last_name?.[0] || ""}`.toUpperCase() || "U";
  const trustRaw = organizer.avg_trust_score;
  const trustValue = trustRaw === null || trustRaw === undefined ? NaN : Number(trustRaw);
  const trustPercent = Number.isFinite(trustValue) ? Math.max(0, Math.min(100, (trustValue / 5) * 100)) : 0;

  return (
    <article
      className="card p-5 hover:shadow-card-hover transition-shadow cursor-pointer"
      onClick={() => router.push(`/organizers/${organizer.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") router.push(`/organizers/${organizer.id}`);
      }}
    >
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-full bg-brand text-white flex items-center justify-center font-medium">
          {initials}
        </div>

        <div className="min-w-0">
          <p className="font-semibold text-neutral-900 truncate">{fullName}</p>
          <p className="text-xs text-neutral-400 truncate">@{organizer.username}</p>
        </div>

        {organizer.is_verified ? (
          <span className="badge bg-success/10 text-success ml-auto shrink-0">✓ Верифицирован</span>
        ) : null}
      </div>

      <div className="mt-2 flex items-center gap-1.5 text-sm text-neutral-500">
        <MapPin className="h-3 w-3 text-neutral-400" />
        <span>{organizer.city || "Город не указан"}</span>
      </div>

      <div className="mt-3 pt-3 border-t border-neutral-200 grid grid-cols-3 gap-2 text-center">
        <div>
          <div className="inline-flex items-center gap-1 text-xs text-neutral-400">
            <Calendar className="h-3 w-3" />
            <span>Мероприятий</span>
          </div>
          <p className="font-semibold text-sm text-neutral-900 mt-1">{organizer.events_count}</p>
        </div>

        <div>
          <div className="inline-flex items-center gap-1 text-xs text-neutral-400">
            <Star className="h-3 w-3" />
            <span>Рейтинг</span>
          </div>
          <p className="font-semibold text-sm text-neutral-700 mt-1">—</p>
        </div>

        <div>
          <div className="inline-flex items-center gap-1 text-xs text-neutral-400">
            <TrendingUp className="h-3 w-3" />
            <span>Рост</span>
          </div>
          <p className="font-semibold text-sm text-neutral-700 mt-1">—</p>
        </div>
      </div>

      {Number.isFinite(trustValue) ? (
        <div className="mt-3">
          <p className="text-xs text-neutral-400 mb-1.5">Рейтинг доверия</p>
          <div className="bg-neutral-100 rounded-full h-1.5 overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                trustPercent >= 70 ? "bg-brand-dark" : "bg-brand"
              )}
              style={{ width: `${trustPercent}%` }}
            />
          </div>
        </div>
      ) : null}
    </article>
  );
}

export default function OrganizersPage() {
  const [organizers, setOrganizers] = useState<OrganizerListWithTrust[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchOrganizers() {
      setLoading(true);
      setError("");
      try {
        const res = await getOrganizers();
        if (!cancelled) {
          setOrganizers(res.data.results ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить список организаторов"
              : "Ошибка соединения с сервером";
          setError(message);
          setOrganizers([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchOrganizers();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return organizers;
    return organizers.filter((organizer) => {
      const fullName = `${organizer.first_name} ${organizer.last_name}`.toLowerCase();
      const username = organizer.username.toLowerCase();
      return fullName.includes(q) || username.includes(q);
    });
  }, [organizers, search]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6 gap-4">
        <h1 className="text-2xl font-semibold text-neutral-900">Организаторы</h1>
        <span className="text-sm text-neutral-500">Найдено: {filtered.length}</span>
      </div>

      <div className="mb-6 max-w-xs relative">
        <Search className="h-4 w-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          className="input pl-9"
          placeholder="Поиск по имени"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? <p className="text-sm text-neutral-500">Загрузка организаторов...</p> : null}
      {error ? <div className="p-3 rounded bg-danger/10 text-danger text-sm mb-4">{error}</div> : null}

      {!loading && !error ? (
        <>
          <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((organizer) => (
              <OrganizerCard key={organizer.id} organizer={organizer} />
            ))}
          </section>
          {filtered.length === 0 ? (
            <p className="text-sm text-neutral-500 mt-6">По выбранному запросу организаторы не найдены.</p>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
