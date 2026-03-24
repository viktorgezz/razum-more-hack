"use client";

import { useEffect, useState } from "react";
import { AxiosError } from "axios";
import { Calendar, Code, Heart, Trophy, Tv } from "lucide-react";

import { getUserRating } from "@/services/ratings";
import { getEvents } from "@/services/events";
import { Event, RatingSnapshot, UserRole } from "@/types";
import { cn, formatDate, formatRating } from "@/lib/utils";

const statusLabel: Record<string, string> = {
  REGISTERED: "Зарегистрирован",
  CHECKED_IN: "Отмечен",
  CONFIRMED: "Подтверждён",
  REJECTED: "Отклонён",
};

const statusColor: Record<string, string> = {
  REGISTERED: "bg-neutral-100 text-neutral-500",
  CHECKED_IN: "bg-info/15 text-info",
  CONFIRMED: "bg-success/15 text-success",
  REJECTED: "bg-danger/10 text-danger",
};

type RatingCardProps = {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  accent?: boolean;
};

function RatingCard({ icon: Icon, label, value, accent }: RatingCardProps) {
  return (
    <div className={cn("card p-4", accent && "border-brand bg-brand-light")}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className={cn("h-4 w-4", accent ? "text-brand" : "text-neutral-500")} />
        <span className="text-xs text-neutral-500">{label}</span>
      </div>
      <p className={cn("text-2xl font-semibold", accent ? "text-brand" : "text-neutral-900")}>
        {formatRating(value)}
      </p>
    </div>
  );
}

export default function ProfilePage() {
  const [username, setUsername] = useState("");
  const [userId, setUserId] = useState<number | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);

  const [rating, setRating] = useState<RatingSnapshot | null>(null);
  const [ratingLoading, setRatingLoading] = useState(true);
  const [ratingError, setRatingError] = useState("");

  const [myEvents, setMyEvents] = useState<Event[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);

  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "User";
    const storedId = Number(localStorage.getItem("user_id"));
    const storedRole = localStorage.getItem("user_role") as UserRole | null;
    setUsername(storedUsername);
    setUserId(storedId || null);
    setRole(storedRole);
  }, []);

  useEffect(() => {
    if (!userId) return;

    if (role === "PARTICIPANT") {
      setRatingLoading(true);
      getUserRating(userId)
        .then((res) => setRating(res.data))
        .catch((err) => {
          if (err instanceof AxiosError && err.response?.status === 404) {
            setRating(null);
          } else {
            setRatingError("Не удалось загрузить рейтинг");
          }
        })
        .finally(() => setRatingLoading(false));
    } else {
      setRatingLoading(false);
    }

    if (role === "ORGANIZER" || role === "ADMIN") {
      setEventsLoading(true);
      getEvents({ organizer_id: userId })
        .then((res) => setMyEvents(res.data.results ?? []))
        .catch(() => setMyEvents([]))
        .finally(() => setEventsLoading(false));
    }
  }, [userId, role]);

  const initials = (username || "U").slice(0, 2).toUpperCase();

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold text-neutral-900 mb-6">Мой профиль</h1>

      <div className="card p-5 mb-6 flex items-center gap-4">
        <div className="h-16 w-16 rounded-full bg-brand text-white text-xl font-semibold flex items-center justify-center shrink-0">
          {initials}
        </div>
        <div>
          <p className="text-lg font-semibold text-neutral-900">{username}</p>
          <p className="text-sm text-neutral-500">{role ?? "—"}</p>
        </div>
      </div>

      {role === "PARTICIPANT" ? (
        <section className="mb-6">
          <h2 className="text-base font-medium text-neutral-900 mb-3">Мой рейтинг</h2>

          {ratingLoading ? <p className="text-sm text-neutral-500">Загрузка рейтинга...</p> : null}
          {ratingError ? <p className="text-sm text-danger">{ratingError}</p> : null}

          {!ratingLoading && !ratingError && !rating ? (
            <div className="card p-4 text-sm text-neutral-500">
              Рейтинг ещё не сформирован — нужно участие в мероприятиях
            </div>
          ) : null}

          {rating ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                <RatingCard icon={Trophy} label="Общий" value={rating.common_rating} accent />
                <RatingCard icon={Code} label="IT" value={rating.rating_it} />
                <RatingCard icon={Heart} label="Социальное" value={rating.rating_social} />
                <RatingCard icon={Tv} label="Медиа" value={rating.rating_media} />
              </div>
              <div className="card p-4 flex items-center gap-4 text-sm">
                <div>
                  <p className="text-xs text-neutral-500">Место в рейтинге</p>
                  <p className="text-2xl font-semibold text-neutral-900">#{rating.rank}</p>
                </div>
                <div>
                  <p className="text-xs text-neutral-500">Дата обновления</p>
                  <p className="font-medium text-neutral-700">{formatDate(rating.snapshot_date)}</p>
                </div>
              </div>
            </>
          ) : null}
        </section>
      ) : null}

      {role === "ORGANIZER" || role === "ADMIN" ? (
        <section className="mb-6">
          <h2 className="text-base font-medium text-neutral-900 mb-3">Мои мероприятия</h2>
          {eventsLoading ? <p className="text-sm text-neutral-500">Загрузка...</p> : null}
          {!eventsLoading && myEvents.length === 0 ? (
            <div className="card p-4 text-sm text-neutral-500">Мероприятий пока нет</div>
          ) : null}
          <div className="space-y-2">
            {myEvents.slice(0, 5).map((event) => (
              <div key={event.id} className="card p-4 flex items-center gap-3 text-sm">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-neutral-900 truncate">{event.name}</p>
                  <div className="flex items-center gap-1.5 text-neutral-500 text-xs mt-0.5">
                    <Calendar className="h-3 w-3" />
                    {formatDate(event.event_date)}
                  </div>
                </div>
                <span className="text-brand font-medium shrink-0">{event.base_points} баллов</span>
              </div>
            ))}
          </div>
          {myEvents.length > 5 ? (
            <p className="text-xs text-neutral-500 mt-2">
              Показано 5 из {myEvents.length}. Полный список — в разделе «Мои мероприятия».
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
