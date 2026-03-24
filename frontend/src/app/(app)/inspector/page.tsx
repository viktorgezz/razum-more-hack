"use client";

import { useEffect, useMemo, useState } from "react";
import { AxiosError } from "axios";
import { FileDown, Lock } from "lucide-react";

import { getCandidates, getCandidateReportUrl } from "@/services/inspector";
import { CandidateList, UserRole } from "@/types";
import { formatDate, getInitials } from "@/lib/utils";

type OrderingValue = "-total_points" | "total_points" | "-events_count" | "-date_joined";

type FilterState = {
  min_avg_points: string;
  max_avg_points: string;
  min_events: string;
  max_events: string;
  ordering: OrderingValue;
};

const PAGE_SIZE = 20;

const initialFilters: FilterState = {
  min_avg_points: "",
  max_avg_points: "",
  min_events: "",
  max_events: "",
  ordering: "-total_points",
};

export default function InspectorPage() {
  const [role, setRole] = useState<UserRole | null>(null);
  const [roleReady, setRoleReady] = useState(false);

  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState<FilterState>(initialFilters);
  const [page, setPage] = useState(1);

  const [items, setItems] = useState<CandidateList[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const localRole = (localStorage.getItem("user_role") as UserRole | null) ?? null;
    setRole(localRole);
    setRoleReady(true);
  }, []);

  const hasAccess = role === "OBSERVER" || role === "ADMIN";

  useEffect(() => {
    if (!roleReady || !hasAccess) return;

    let cancelled = false;
    async function loadCandidates() {
      setLoading(true);
      setError("");

      try {
        const res = await getCandidates({
          page,
          ordering: appliedFilters.ordering,
          min_avg_points: appliedFilters.min_avg_points ? Number(appliedFilters.min_avg_points) : undefined,
          max_avg_points: appliedFilters.max_avg_points ? Number(appliedFilters.max_avg_points) : undefined,
          min_events: appliedFilters.min_events ? Number(appliedFilters.min_events) : undefined,
          max_events: appliedFilters.max_events ? Number(appliedFilters.max_events) : undefined,
        });

        if (!cancelled) {
          setItems(res.data.results ?? []);
          setTotalCount(res.data.count ?? 0);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить кандидатов"
              : "Ошибка соединения с сервером";
          setError(message);
          setItems([]);
          setTotalCount(0);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadCandidates();
    return () => {
      cancelled = true;
    };
  }, [page, appliedFilters, roleReady, hasAccess]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  const pageNumbers = useMemo(() => Array.from({ length: totalPages }, (_, i) => i + 1), [totalPages]);

  async function handleDownloadPdf(candidateId: number) {
    const token = localStorage.getItem("access_token");
    const url = getCandidateReportUrl(candidateId);
    try {
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!res.ok) throw new Error("Failed to download PDF");

      const blob = await res.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      window.open(objectUrl, "_blank", "noopener,noreferrer");
      setTimeout(() => window.URL.revokeObjectURL(objectUrl), 30_000);
    } catch {
      setError("Не удалось скачать PDF-отчёт");
    }
  }

  function applyFilters() {
    setAppliedFilters(filters);
    setPage(1);
  }

  function resetFilters() {
    setFilters(initialFilters);
    setAppliedFilters(initialFilters);
    setPage(1);
  }

  if (!roleReady) {
    return <p className="text-sm text-neutral-500">Проверка доступа...</p>;
  }

  if (!hasAccess) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-center">
        <Lock className="h-12 w-12 text-neutral-300" />
        <p className="text-lg font-medium mt-4 text-neutral-900">Доступ ограничен</p>
        <p className="text-sm text-neutral-500">Раздел доступен кадровой службе и администраторам</p>
      </div>
    );
  }

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Кадровый резерв</h1>
        <p className="text-sm text-neutral-500">Расширенная аналитика кандидатов</p>
      </header>

      <section className="card p-4 mb-6">
        <h2 className="text-sm font-medium mb-3 text-neutral-900">Фильтры</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <input
            type="number"
            className="input"
            placeholder="Мин. баллов"
            value={filters.min_avg_points}
            onChange={(e) => setFilters((prev) => ({ ...prev, min_avg_points: e.target.value }))}
          />
          <input
            type="number"
            className="input"
            placeholder="Макс. баллов"
            value={filters.max_avg_points}
            onChange={(e) => setFilters((prev) => ({ ...prev, max_avg_points: e.target.value }))}
          />
          <input
            type="number"
            className="input"
            placeholder="Мин. мероприятий"
            value={filters.min_events}
            onChange={(e) => setFilters((prev) => ({ ...prev, min_events: e.target.value }))}
          />
          <input
            type="number"
            className="input"
            placeholder="Макс. мероприятий"
            value={filters.max_events}
            onChange={(e) => setFilters((prev) => ({ ...prev, max_events: e.target.value }))}
          />
          <select
            className="input md:col-span-2"
            value={filters.ordering}
            onChange={(e) => setFilters((prev) => ({ ...prev, ordering: e.target.value as OrderingValue }))}
          >
            <option value="-total_points">Больше баллов</option>
            <option value="total_points">Меньше баллов</option>
            <option value="-events_count">Больше мероприятий</option>
            <option value="-date_joined">Дата регистрации</option>
          </select>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <button type="button" className="btn-primary" onClick={applyFilters}>
            Применить
          </button>
          <button type="button" className="btn-secondary" onClick={resetFilters}>
            Сбросить
          </button>
        </div>
      </section>

      {error ? <div className="mb-4 p-3 rounded bg-danger/10 text-danger text-sm">{error}</div> : null}

      <section className="card overflow-x-auto">
        <div className="min-w-[980px]">
          <div className="text-xs uppercase text-neutral-500 bg-neutral-50 border-b border-neutral-200 grid grid-cols-[2fr_2fr_1.2fr_1fr_1fr_1.2fr_1.2fr_1fr] gap-3 px-4 py-3">
            <span>Участник</span>
            <span>Email</span>
            <span>Дата вступления</span>
            <span>Мероприятий</span>
            <span>Подтв.</span>
            <span>Всего баллов</span>
            <span>Средний балл</span>
            <span>Действия</span>
          </div>

          {loading ? (
            <div className="px-4 py-6 text-sm text-neutral-500">Загрузка кандидатов...</div>
          ) : items.length === 0 ? (
            <div className="px-4 py-6 text-sm text-neutral-500">Кандидаты не найдены.</div>
          ) : (
            items.map((candidate) => {
              const fullName =
                `${candidate.first_name} ${candidate.last_name}`.trim() ||
                candidate.username ||
                `ID ${candidate.id}`;
              return (
                <div
                  key={candidate.id}
                  className="border-b border-neutral-100 hover:bg-neutral-50/50 transition-colors grid grid-cols-[2fr_2fr_1.2fr_1fr_1fr_1.2fr_1.2fr_1fr] gap-3 px-4 py-3 items-center"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="h-8 w-8 rounded-full bg-brand text-white text-xs font-semibold flex items-center justify-center shrink-0">
                      {getInitials(candidate.first_name, candidate.last_name) || getInitials(candidate.username, "")}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-neutral-900 truncate">{fullName}</p>
                      <p className="text-xs text-neutral-500 truncate">@{candidate.username}</p>
                    </div>
                  </div>

                  <span className="text-sm text-neutral-700 truncate">{candidate.email}</span>
                  <span className="text-sm text-neutral-600">{formatDate(candidate.date_joined)}</span>
                  <span className="text-sm text-neutral-700">{candidate.events_count}</span>
                  <span className="text-sm text-success font-medium">{candidate.confirmed_count}</span>
                  <span className="text-sm text-neutral-900 font-medium">{candidate.total_points}</span>
                  <span className="text-sm text-neutral-900">{Number(candidate.avg_points).toFixed(1)}</span>

                  <button
                    type="button"
                    className="btn-secondary text-xs px-2 py-1 inline-flex items-center gap-1.5 w-fit"
                    onClick={() => handleDownloadPdf(candidate.id)}
                  >
                    <FileDown className="h-3.5 w-3.5" />
                    PDF
                  </button>
                </div>
              );
            })
          )}
        </div>
      </section>

      <div className="mt-6 flex items-center gap-2 flex-wrap">
        <button
          type="button"
          className="btn-secondary"
          disabled={page <= 1}
          onClick={() => setPage((prev) => Math.max(1, prev - 1))}
        >
          ← Назад
        </button>

        {pageNumbers.map((pageNumber) => (
          <button
            key={pageNumber}
            type="button"
            onClick={() => setPage(pageNumber)}
            className={`px-3 py-2 rounded text-sm border transition-colors ${
              pageNumber === page
                ? "bg-brand text-white border-brand"
                : "bg-white text-neutral-700 border-neutral-300 hover:bg-neutral-50"
            }`}
          >
            {pageNumber}
          </button>
        ))}

        <button
          type="button"
          className="btn-secondary"
          disabled={page >= totalPages}
          onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
        >
          Вперёд →
        </button>
      </div>
    </div>
  );
}
