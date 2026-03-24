"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Calendar, Gift, Search } from "lucide-react";
import { AxiosError } from "axios";

import { getEvents } from "@/services/events";
import { Event, EventStatus, EventType, PaginatedResponse } from "@/types";
import { cn, formatDate } from "@/lib/utils";

const PAGE_SIZE = 20;

const typeLabelMap: Record<EventType, string> = {
  LECTURE: "Лекция",
  HACKATHON: "Хакатон",
  FORUM: "Форум",
  VOLUNTEER: "Волонтёрство",
  OTHER: "Другое",
};

const statusLabelMap: Record<EventStatus, string> = {
  DRAFT: "Черновик",
  PUBLISHED: "Опубликовано",
  ONGOING: "Идёт",
  COMPLETED: "Завершено",
  CANCELLED: "Отменено",
};

const statusColorMap: Record<EventStatus, string> = {
  PUBLISHED: "bg-info/15 text-info",
  ONGOING: "bg-success/15 text-success",
  COMPLETED: "bg-neutral-100 text-neutral-500",
  DRAFT: "bg-neutral-100 text-neutral-400",
  CANCELLED: "bg-danger/10 text-danger",
};

function getCategoryColor(slug?: string | null) {
  if (slug === "it") return "bg-brand";
  if (slug === "social") return "bg-success";
  if (slug === "media") return "bg-warning";
  return "bg-neutral-300";
}

function EventCard({ event }: { event: Event }) {
  const router = useRouter();
  return (
    <article
      className="card hover:shadow-card-hover transition-shadow p-5 cursor-pointer"
      onClick={() => router.push(`/events/${event.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") router.push(`/events/${event.id}`); }}
    >
      <div className={cn("h-1 rounded-t-lg -mt-5 -mx-5 mb-4", getCategoryColor(event.category?.slug))} />

      <div className="flex items-center justify-between gap-2">
        <span className="badge bg-brand-light text-brand">{typeLabelMap[event.event_type] ?? event.event_type}</span>
        <span className={cn("badge", statusColorMap[event.status] ?? "bg-neutral-100 text-neutral-500")}>
          {statusLabelMap[event.status] ?? event.status}
        </span>
      </div>

      <h3 className="font-semibold text-base mt-2 line-clamp-2 text-neutral-900">{event.name}</h3>

      <div className="text-sm text-neutral-500 mt-1 flex items-center gap-1.5">
        <Calendar className="h-3.5 w-3.5" />
        <span>{formatDate(event.event_date)}</span>
      </div>

      <p className="text-xs text-neutral-400 mt-0.5">{event.category?.name ?? "Без категории"}</p>
      <p className="text-sm text-neutral-600 mt-2 line-clamp-2">{event.description}</p>

      <div className="mt-3 pt-3 border-t border-neutral-200 flex justify-between items-center text-sm">
        <div className="flex items-center gap-2">
          <span className="text-brand font-medium">{"⚡"} {event.base_points} баллов</span>
          {event.prizes?.length > 0 ? (
            <span className="inline-flex items-center gap-1 text-warning text-xs">
              <Gift className="h-3.5 w-3.5" />
              {event.prizes.length}
            </span>
          ) : null}
        </div>
        <span className="text-neutral-400 text-xs">{"×"} {event.difficulty_coef}</span>
      </div>
    </article>
  );
}

export default function EventsPage() {
  const [data, setData] = useState<PaginatedResponse<Event> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [eventType, setEventType] = useState<"" | EventType>("");
  const [status, setStatus] = useState<"" | "PUBLISHED" | "ONGOING" | "COMPLETED">("");
  const [ordering, setOrdering] = useState<"event_date" | "-event_date" | "base_points" | "-base_points">(
    "-event_date"
  );

  useEffect(() => {
    let cancelled = false;

    async function fetchEvents() {
      setLoading(true);
      setError("");

      try {
        const response = await getEvents({
          page,
          ordering,
          event_type: eventType || undefined,
          status: status || undefined,
        });
        if (!cancelled) {
          setData(response.data);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить мероприятия"
              : "Ошибка соединения с сервером";
          setError(message);
          setData(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchEvents();

    return () => {
      cancelled = true;
    };
  }, [page, eventType, status, ordering]);

  const filteredEvents = useMemo(() => {
    const items = data?.results ?? [];
    const normalized = search.trim().toLowerCase();
    if (!normalized) return items;
    return items.filter((event) => event.name.toLowerCase().includes(normalized));
  }, [data?.results, search]);

  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / PAGE_SIZE));
  const pageNumbers = useMemo(() => Array.from({ length: totalPages }, (_, idx) => idx + 1), [totalPages]);

  function resetFilters() {
    setSearch("");
    setEventType("");
    setStatus("");
    setOrdering("-event_date");
    setPage(1);
  }

  function onChangeType(value: "" | EventType) {
    setEventType(value);
    setPage(1);
  }

  function onChangeStatus(value: "" | "PUBLISHED" | "ONGOING" | "COMPLETED") {
    setStatus(value);
    setPage(1);
  }

  function onChangeOrdering(value: "event_date" | "-event_date" | "base_points" | "-base_points") {
    setOrdering(value);
    setPage(1);
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6 gap-4">
        <h1 className="text-2xl font-semibold text-neutral-900">Мероприятия</h1>
        <span className="text-sm text-neutral-500">Найдено: {filteredEvents.length}</span>
      </div>

      <section className="card p-4 mb-6 flex flex-wrap gap-3">
        <div className="relative min-w-60 flex-1">
          <Search className="h-4 w-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            className="input pl-9"
            placeholder="Поиск по названию"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          className="input w-auto min-w-48"
          value={eventType}
          onChange={(e) => onChangeType(e.target.value as "" | EventType)}
        >
          <option value="">Все типы</option>
          <option value="LECTURE">Лекция</option>
          <option value="HACKATHON">Хакатон</option>
          <option value="FORUM">Форум</option>
          <option value="VOLUNTEER">Волонтёрство</option>
          <option value="OTHER">Другое</option>
        </select>

        <select
          className="input w-auto min-w-44"
          value={status}
          onChange={(e) => onChangeStatus(e.target.value as "" | "PUBLISHED" | "ONGOING" | "COMPLETED")}
        >
          <option value="">Статус</option>
          <option value="PUBLISHED">Опубликовано</option>
          <option value="ONGOING">Идёт</option>
          <option value="COMPLETED">Завершено</option>
        </select>

        <select
          className="input w-auto min-w-52"
          value={ordering}
          onChange={(e) =>
            onChangeOrdering(e.target.value as "event_date" | "-event_date" | "base_points" | "-base_points")
          }
        >
          <option value="-event_date">Сначала новые даты</option>
          <option value="event_date">Сначала старые даты</option>
          <option value="-base_points">Больше баллов</option>
          <option value="base_points">Меньше баллов</option>
        </select>

        <button type="button" className="btn-secondary" onClick={resetFilters}>
          Сбросить
        </button>
      </section>

      {loading ? <p className="text-sm text-neutral-500">Загрузка мероприятий...</p> : null}
      {error ? <div className="p-3 rounded bg-danger/10 text-danger text-sm mb-4">{error}</div> : null}

      {!loading && !error ? (
        <>
          <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </section>

          {filteredEvents.length === 0 ? (
            <p className="text-sm text-neutral-500 mt-6">По выбранным фильтрам мероприятий не найдено.</p>
          ) : null}

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
                className={cn(
                  "px-3 py-2 rounded text-sm border transition-colors",
                  pageNumber === page
                    ? "bg-brand text-white border-brand"
                    : "bg-white text-neutral-700 border-neutral-300 hover:bg-neutral-50"
                )}
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
        </>
      ) : null}
    </div>
  );
}
