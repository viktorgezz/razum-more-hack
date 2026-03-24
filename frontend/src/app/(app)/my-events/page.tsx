"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { ChevronDown, ChevronUp, Plus, UserCheck, X } from "lucide-react";

import {
  confirmParticipant,
  createEvent,
  deleteEvent,
  getEventParticipants,
  getEvents,
  organizerCheckin,
  updateEvent,
} from "@/services/events";
import { Event, EventParticipant, EventStatus, EventType, UserRole } from "@/types";
import { cn, formatDate } from "@/lib/utils";

const statusLabel: Record<EventStatus, string> = {
  DRAFT: "Черновик",
  PUBLISHED: "Опубликовано",
  ONGOING: "Идёт",
  COMPLETED: "Завершено",
  CANCELLED: "Отменено",
};

const statusColor: Record<EventStatus, string> = {
  DRAFT: "bg-neutral-100 text-neutral-400",
  PUBLISHED: "bg-info/15 text-info",
  ONGOING: "bg-success/15 text-success",
  COMPLETED: "bg-neutral-100 text-neutral-500",
  CANCELLED: "bg-danger/10 text-danger",
};

const participantStatusLabel: Record<string, string> = {
  REGISTERED: "Зарегистрирован",
  CHECKED_IN: "Отмечен",
  CONFIRMED: "Подтверждён",
  REJECTED: "Отклонён",
};

type FormData = {
  name: string;
  description: string;
  event_date: string;
  event_type: EventType;
  difficulty_coef: string;
  base_points: string;
  max_participants: string;
  status: EventStatus;
};

const emptyForm: FormData = {
  name: "",
  description: "",
  event_date: "",
  event_type: "LECTURE",
  difficulty_coef: "1.0",
  base_points: "10",
  max_participants: "100",
  status: "DRAFT",
};

function EventForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: FormData;
  onSave: (data: FormData) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<FormData>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function set(field: keyof FormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await onSave(form);
    } catch (err) {
      setError(
        err instanceof AxiosError && err.response?.data
          ? JSON.stringify(err.response.data)
          : "Не удалось сохранить"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card p-5 mb-4 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm text-neutral-700 mb-1">Название</label>
          <input className="input" required value={form.name} onChange={(e) => set("name", e.target.value)} />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-neutral-700 mb-1">Описание</label>
          <textarea className="input min-h-20 resize-y" value={form.description} onChange={(e) => set("description", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Дата проведения</label>
          <input type="datetime-local" className="input" required value={form.event_date} onChange={(e) => set("event_date", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Тип</label>
          <select className="input" value={form.event_type} onChange={(e) => set("event_type", e.target.value as EventType)}>
            <option value="LECTURE">Лекция</option>
            <option value="HACKATHON">Хакатон</option>
            <option value="FORUM">Форум</option>
            <option value="VOLUNTEER">Волонтёрство</option>
            <option value="OTHER">Другое</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Базовые баллы</label>
          <input type="number" min="1" className="input" value={form.base_points} onChange={(e) => set("base_points", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Коэффициент сложности</label>
          <input type="number" min="0.1" step="0.1" className="input" value={form.difficulty_coef} onChange={(e) => set("difficulty_coef", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Макс. участников</label>
          <input type="number" min="1" className="input" value={form.max_participants} onChange={(e) => set("max_participants", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-neutral-700 mb-1">Статус</label>
          <select className="input" value={form.status} onChange={(e) => set("status", e.target.value as EventStatus)}>
            <option value="DRAFT">Черновик</option>
            <option value="PUBLISHED">Опубликовать</option>
            <option value="ONGOING">Идёт</option>
            <option value="COMPLETED">Завершено</option>
            <option value="CANCELLED">Отменено</option>
          </select>
        </div>
      </div>
      {error ? <p className="text-sm text-danger">{error}</p> : null}
      <div className="flex gap-2">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Сохранение..." : "Сохранить"}
        </button>
        <button type="button" className="btn-secondary" onClick={onCancel}>Отмена</button>
      </div>
    </form>
  );
}

function ParticipantsPanel({ eventId }: { eventId: number }) {
  const [participants, setParticipants] = useState<EventParticipant[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState<number | null>(null);
  const [qrInput, setQrInput] = useState("");
  const [qrLoading, setQrLoading] = useState(false);
  const [qrMessage, setQrMessage] = useState("");
  const [qrError, setQrError] = useState("");

  useEffect(() => {
    getEventParticipants(eventId)
      .then((res) => setParticipants(Array.isArray(res.data) ? res.data : []))
      .catch(() => setParticipants([]))
      .finally(() => setLoading(false));
  }, [eventId]);

  async function handleConfirm(userId: number) {
    setConfirming(userId);
    try {
      await confirmParticipant(eventId, userId);
      setParticipants((prev) =>
        prev.map((p) => (p.user_id === userId ? { ...p, status: "CONFIRMED" as const } : p))
      );
    } catch {
      // ignore
    } finally {
      setConfirming(null);
    }
  }

  async function handleQrCheckin() {
    if (!qrInput.trim()) return;
    setQrLoading(true);
    setQrMessage("");
    setQrError("");
    try {
      const res = await organizerCheckin(eventId, qrInput.trim());
      const p = res.data;
      const name = `${p.first_name} ${p.last_name}`.trim() || p.username;
      setQrMessage(`Отмечен: ${name}`);
      setQrInput("");
      setParticipants((prev) =>
        prev.map((part) => (part.user_id === p.user_id ? { ...part, status: "CHECKED_IN" as const } : part))
      );
    } catch (err) {
      const axErr = err instanceof (await import("axios")).AxiosError ? err as import("axios").AxiosError : null;
      const data = axErr?.response?.data as Record<string, unknown> | undefined;
      setQrError((data?.detail as string) ?? "Неверный QR-код");
    } finally {
      setQrLoading(false);
    }
  }

  if (loading) return <p className="text-xs text-neutral-500 px-4 py-2">Загрузка участников...</p>;

  return (
    <div className="border-t border-neutral-100 bg-neutral-50/50">
      {/* QR-сканер организатора */}
      <div className="px-4 py-3 border-b border-neutral-200 bg-white">
        <p className="text-xs font-medium text-neutral-700 mb-2">Сканирование QR-кода участника</p>
        <div className="flex gap-2">
          <input
            className="input text-sm flex-1"
            placeholder="Вставьте или введите QR-код участника"
            value={qrInput}
            onChange={(e) => setQrInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") void handleQrCheckin(); }}
          />
          <button
            type="button"
            className="btn-primary text-sm px-3 disabled:opacity-50"
            onClick={handleQrCheckin}
            disabled={qrLoading || !qrInput.trim()}
          >
            {qrLoading ? "..." : "Отметить"}
          </button>
        </div>
        {qrMessage ? <p className="text-xs text-success mt-1">{qrMessage}</p> : null}
        {qrError ? <p className="text-xs text-danger mt-1">{qrError}</p> : null}
      </div>

      {participants.length === 0 ? (
        <p className="text-xs text-neutral-500 px-4 py-2">Участников пока нет</p>
      ) : null}

      {participants.map((p) => {
        const name = `${p.first_name} ${p.last_name}`.trim() || p.username;
        return (
          <div key={p.id} className="flex items-center gap-3 px-4 py-2 text-sm border-b border-neutral-100 last:border-0">
            <div className="flex-1 min-w-0">
              <span className="font-medium text-neutral-900">{name}</span>
              <span className="text-neutral-400 ml-1">@{p.username}</span>
            </div>
            <span className={cn(
              "badge text-xs",
              p.status === "CONFIRMED" ? "bg-success/10 text-success"
              : p.status === "CHECKED_IN" ? "bg-info/10 text-info"
              : p.status === "REJECTED" ? "bg-danger/10 text-danger"
              : "bg-neutral-100 text-neutral-500"
            )}>
              {participantStatusLabel[p.status]}
            </span>
            {(p.status === "REGISTERED" || p.status === "CHECKED_IN") ? (
              <button
                type="button"
                className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-success/10 text-success rounded hover:bg-success/20 disabled:opacity-50"
                onClick={() => handleConfirm(p.user_id)}
                disabled={confirming === p.user_id}
              >
                <UserCheck className="h-3.5 w-3.5" />
                Подтвердить
              </button>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

export default function MyEventsPage() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole | null>(null);
  const [organizerId, setOrganizerId] = useState<number | null>(null);

  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    const r = localStorage.getItem("user_role") as UserRole | null;
    const id = Number(localStorage.getItem("user_id"));
    setRole(r);
    setOrganizerId(id || null);
    if (r !== "ORGANIZER" && r !== "ADMIN") {
      router.replace("/events");
    }
  }, [router]);

  useEffect(() => {
    if (!organizerId) return;
    setLoading(true);
    getEvents({ organizer_id: organizerId })
      .then((res) => setEvents(res.data.results ?? []))
      .catch(() => setError("Не удалось загрузить мероприятия"))
      .finally(() => setLoading(false));
  }, [organizerId]);

  async function handleCreate(data: FormData) {
    const res = await createEvent({
      name: data.name,
      description: data.description,
      event_date: new Date(data.event_date).toISOString(),
      event_type: data.event_type,
      difficulty_coef: data.difficulty_coef,
      base_points: Number(data.base_points),
      max_participants: Number(data.max_participants),
      status: data.status,
    });
    setEvents((prev) => [res.data, ...prev]);
    setShowForm(false);
  }

  async function handleUpdate(data: FormData) {
    if (!editingEvent) return;
    const res = await updateEvent(editingEvent.id, {
      name: data.name,
      description: data.description,
      event_date: new Date(data.event_date).toISOString(),
      event_type: data.event_type,
      difficulty_coef: data.difficulty_coef,
      base_points: Number(data.base_points),
      max_participants: Number(data.max_participants),
      status: data.status,
    });
    setEvents((prev) => prev.map((e) => (e.id === editingEvent.id ? res.data : e)));
    setEditingEvent(null);
  }

  async function handleDelete(id: number) {
    if (!confirm("Удалить мероприятие?")) return;
    setDeletingId(id);
    try {
      await deleteEvent(id);
      setEvents((prev) => prev.filter((e) => e.id !== id));
    } catch {
      // ignore
    } finally {
      setDeletingId(null);
    }
  }

  if (role !== "ORGANIZER" && role !== "ADMIN") return null;

  return (
    <div>
      <header className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900">Мои мероприятия</h1>
          <p className="text-sm text-neutral-500">Управление мероприятиями</p>
        </div>
        <button
          type="button"
          className="btn-primary inline-flex items-center gap-2"
          onClick={() => { setShowForm(true); setEditingEvent(null); }}
        >
          <Plus className="h-4 w-4" />
          Создать мероприятие
        </button>
      </header>

      {showForm && !editingEvent ? (
        <EventForm
          initial={emptyForm}
          onSave={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      ) : null}

      {loading ? <p className="text-sm text-neutral-500">Загрузка...</p> : null}
      {error ? <div className="p-3 rounded bg-danger/10 text-danger text-sm">{error}</div> : null}

      {!loading && events.length === 0 && !error ? (
        <div className="card p-10 text-center text-neutral-500 text-sm">
          У вас пока нет мероприятий. Создайте первое!
        </div>
      ) : null}

      <div className="space-y-2">
        {events.map((event) => {
          const isExpanded = expandedId === event.id;
          const isEditing = editingEvent?.id === event.id;

          return (
            <div key={event.id} className="card overflow-hidden">
              {isEditing ? (
                <div className="p-4">
                  <EventForm
                    initial={{
                      name: event.name,
                      description: event.description,
                      event_date: event.event_date.slice(0, 16),
                      event_type: event.event_type,
                      difficulty_coef: event.difficulty_coef,
                      base_points: String(event.base_points),
                      max_participants: String(event.max_participants ?? 100),
                      status: event.status,
                    }}
                    onSave={handleUpdate}
                    onCancel={() => setEditingEvent(null)}
                  />
                </div>
              ) : (
                <div className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-medium text-neutral-900 truncate">{event.name}</h3>
                        <span className={cn("badge text-xs", statusColor[event.status])}>
                          {statusLabel[event.status]}
                        </span>
                      </div>
                      <p className="text-xs text-neutral-500 mt-0.5">
                        {formatDate(event.event_date)} · {event.base_points} баллов · ×{event.difficulty_coef}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <button
                        type="button"
                        className="px-2 py-1 text-xs bg-neutral-100 text-neutral-600 rounded hover:bg-neutral-200"
                        onClick={() => { setEditingEvent(event); setShowForm(false); }}
                      >
                        Изменить
                      </button>
                      <button
                        type="button"
                        className="p-1.5 text-neutral-400 hover:text-danger rounded hover:bg-danger/10 disabled:opacity-50"
                        onClick={() => handleDelete(event.id)}
                        disabled={deletingId === event.id}
                        title="Удалить"
                      >
                        <X className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        className="p-1.5 text-neutral-400 hover:text-neutral-700 rounded hover:bg-neutral-100"
                        onClick={() => setExpandedId(isExpanded ? null : event.id)}
                        title={isExpanded ? "Скрыть участников" : "Показать участников"}
                      >
                        {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              )}
              {isExpanded && !isEditing ? <ParticipantsPanel eventId={event.id} /> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
