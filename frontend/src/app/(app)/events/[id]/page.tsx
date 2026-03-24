"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { ArrowLeft, Calendar, Gift, QrCode, Users } from "lucide-react";
import QRCode from "qrcode";

import { getEvent, getMyParticipation, registerForEvent } from "@/services/events";
import { Event, EventStatus, EventType, Participation, UserRole } from "@/types";
import { cn, formatDate } from "@/lib/utils";

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

const participationStatusLabel: Record<string, string> = {
  REGISTERED: "Зарегистрирован",
  CHECKED_IN: "Присутствие отмечено",
  CONFIRMED: "Участие подтверждено",
  REJECTED: "Отклонён",
};

const prizeTypeLabelMap: Record<string, string> = {
  MERCH: "Мерч",
  TICKETS: "Билеты",
  INTERNSHIP: "Стажировка",
  GRANT: "Грант",
  MEETING: "Встреча",
};

function QRDisplay({ token }: { token: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !token) return;
    QRCode.toCanvas(canvasRef.current, token, {
      width: 200,
      margin: 2,
      color: { dark: "#000000", light: "#ffffff" },
    }).catch(console.error);
  }, [token]);

  return (
    <div className="flex flex-col items-center gap-2">
      <canvas ref={canvasRef} className="rounded border border-neutral-200" />
      <p className="text-xs text-neutral-400 font-mono break-all max-w-52 text-center">{token}</p>
    </div>
  );
}

export default function EventDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const eventId = Number(params?.id);

  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [role, setRole] = useState<UserRole | null>(null);
  const [participation, setParticipation] = useState<Participation | null>(null);
  const [partLoading, setPartLoading] = useState(false);

  const [registering, setRegistering] = useState(false);
  const [registerError, setRegisterError] = useState("");

  useEffect(() => {
    setRole((localStorage.getItem("user_role") as UserRole | null) ?? null);
  }, []);

  useEffect(() => {
    if (!Number.isFinite(eventId)) {
      setError("Некорректный ID мероприятия");
      setLoading(false);
      return;
    }
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const res = await getEvent(eventId);
        if (!cancelled) setEvent(res.data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить мероприятие"
              : "Ошибка соединения с сервером"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, [eventId]);

  // Загружаем существующее участие для участника
  useEffect(() => {
    setParticipation(null);
    if (role !== "PARTICIPANT" || !Number.isFinite(eventId)) return;
    let cancelled = false;
    setPartLoading(true);
    getMyParticipation(eventId)
      .then((res) => { if (!cancelled) setParticipation(res.data); })
      .catch(() => { if (!cancelled) setParticipation(null); })
      .finally(() => { if (!cancelled) setPartLoading(false); });
    return () => { cancelled = true; };
  }, [eventId, role]);

  async function handleRegister() {
    setRegistering(true);
    setRegisterError("");
    try {
      const res = await registerForEvent(eventId);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setParticipation(res.data as any);
    } catch (err) {
      const axErr = err instanceof AxiosError ? err : null;
      const detail = axErr?.response?.data?.detail ?? axErr?.response?.data ?? null;
      setRegisterError(detail ? String(detail) : "Не удалось зарегистрироваться");
    } finally {
      setRegistering(false);
    }
  }

  if (loading) return <p className="text-sm text-neutral-500">Загрузка...</p>;
  if (error || !event) {
    return <div className="p-3 rounded bg-danger/10 text-danger text-sm">{error || "Мероприятие не найдено"}</div>;
  }

  const canRegister =
    role === "PARTICIPANT" &&
    (event.status === "PUBLISHED" || event.status === "ONGOING") &&
    !participation;

  return (
    <div className="max-w-2xl">
      <button
        type="button"
        onClick={() => router.back()}
        className="inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-900 mb-4"
      >
        <ArrowLeft className="h-4 w-4" />
        Назад
      </button>

      {/* Основная карточка */}
      <div className="card p-6 mb-4">
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <span className="badge bg-brand-light text-brand">{typeLabelMap[event.event_type] ?? event.event_type}</span>
          <span className={cn("badge", statusColorMap[event.status] ?? "bg-neutral-100 text-neutral-500")}>
            {statusLabelMap[event.status] ?? event.status}
          </span>
          {event.category ? (
            <span className="badge bg-neutral-100 text-neutral-600">{event.category.name}</span>
          ) : null}
        </div>

        <h1 className="text-2xl font-semibold text-neutral-900">{event.name}</h1>

        <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-neutral-500">
          <span className="inline-flex items-center gap-1.5">
            <Calendar className="h-4 w-4" />
            {formatDate(event.event_date)}
          </span>
          {event.max_participants ? (
            <span className="inline-flex items-center gap-1.5">
              <Users className="h-4 w-4" />
              Макс. {event.max_participants} участников
            </span>
          ) : null}
        </div>

        {event.description ? (
          <p className="mt-4 text-neutral-700 leading-relaxed">{event.description}</p>
        ) : null}

        <div className="mt-4 pt-4 border-t border-neutral-200 flex items-center gap-6">
          <div>
            <p className="text-xs text-neutral-400">Баллы</p>
            <p className="text-lg font-semibold text-brand">{event.base_points}</p>
          </div>
          <div>
            <p className="text-xs text-neutral-400">Коэффициент</p>
            <p className="text-lg font-semibold text-neutral-900">×{event.difficulty_coef}</p>
          </div>
          <div>
            <p className="text-xs text-neutral-400">Итого</p>
            <p className="text-lg font-semibold text-neutral-900">
              {(event.base_points * Number(event.difficulty_coef)).toFixed(0)}
            </p>
          </div>
        </div>
      </div>

      {/* Призы */}
      {event.prizes && event.prizes.length > 0 ? (
        <div className="card p-5 mb-4">
          <h2 className="font-medium text-neutral-900 mb-3 flex items-center gap-2">
            <Gift className="h-4 w-4 text-warning" />
            Призы
          </h2>
          <div className="flex flex-col gap-2">
            {event.prizes.map((prize) => (
              <div key={prize.id} className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium text-neutral-900">{prize.name}</span>
                  {prize.description && prize.description !== prize.name ? (
                    <span className="text-neutral-500 ml-2">{prize.description}</span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="badge bg-warning/10 text-warning">
                    {prizeTypeLabelMap[prize.prize_type] ?? prize.prize_type}
                  </span>
                  <span className="text-neutral-400 text-xs">{prize.quantity} шт.</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Блок участия — только для участников */}
      {role === "PARTICIPANT" ? (
        <div className="card p-5">
          <h2 className="font-medium text-neutral-900 mb-4 flex items-center gap-2">
            <QrCode className="h-4 w-4" />
            Моё участие
          </h2>

          {partLoading ? (
            <p className="text-sm text-neutral-500">Загрузка...</p>
          ) : participation ? (
            <div className="flex flex-col items-center gap-4">
              <div className={cn(
                "w-full text-center py-2 rounded text-sm font-medium",
                participation.status === "CONFIRMED" ? "bg-success/10 text-success"
                : participation.status === "CHECKED_IN" ? "bg-info/10 text-info"
                : participation.status === "REJECTED" ? "bg-danger/10 text-danger"
                : "bg-neutral-100 text-neutral-600"
              )}>
                {participationStatusLabel[participation.status] ?? participation.status}
              </div>

              {participation.status !== "CONFIRMED" && participation.status !== "REJECTED" ? (
                <>
                  <p className="text-sm text-neutral-500 text-center">
                    Покажи этот QR-код организатору при прибытии на мероприятие
                  </p>
                  <QRDisplay token={participation.qr_token} />
                </>
              ) : null}

              {participation.status === "CONFIRMED" && participation.points_awarded > 0 ? (
                <p className="text-sm text-success font-medium">
                  Начислено баллов: {participation.points_awarded}
                </p>
              ) : null}
            </div>
          ) : canRegister ? (
            <>
              {registerError ? (
                <p className="text-sm text-danger mb-2">{registerError}</p>
              ) : null}
              <button
                type="button"
                className="btn-primary w-full"
                onClick={handleRegister}
                disabled={registering}
              >
                {registering ? "Регистрация..." : "Зарегистрироваться"}
              </button>
            </>
          ) : (
            <p className="text-sm text-neutral-400">
              {event.status === "COMPLETED" || event.status === "CANCELLED"
                ? "Регистрация на это мероприятие закрыта"
                : "Регистрация недоступна"}
            </p>
          )}
        </div>
      ) : null}
    </div>
  );
}
