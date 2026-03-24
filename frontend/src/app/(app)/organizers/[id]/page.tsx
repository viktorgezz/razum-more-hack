"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AxiosError } from "axios";
import { Calendar, CheckCircle, Gift, MapPin, Star } from "lucide-react";

import {
  createReview,
  getOrganizerEvents,
  getOrganizerProfile,
  getOrganizerReviews,
} from "@/services/organizers";
import { OrganizerEvent, OrganizerProfile, OrganizerReview, UserRole } from "@/types";
import { formatDate, getInitials } from "@/lib/utils";

type TabKey = "events" | "reviews";

const typeLabelMap: Record<OrganizerEvent["event_type"], string> = {
  LECTURE: "Лекция",
  HACKATHON: "Хакатон",
  FORUM: "Форум",
  VOLUNTEER: "Волонтёрство",
  OTHER: "Другое",
};

function Stars({ value, size = 16 }: { value: number; size?: number }) {
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }, (_, idx) => idx + 1).map((starValue) => (
        <Star
          key={starValue}
          className={starValue <= value ? "text-yellow-400 fill-yellow-400" : "text-neutral-200"}
          size={size}
        />
      ))}
    </div>
  );
}

export default function OrganizerProfilePage() {
  const params = useParams<{ id: string }>();
  const organizerId = Number(params?.id);

  const [profile, setProfile] = useState<OrganizerProfile | null>(null);
  const [events, setEvents] = useState<OrganizerEvent[]>([]);
  const [reviews, setReviews] = useState<OrganizerReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState<TabKey>("events");

  const [role, setRole] = useState<UserRole | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<number | "">("");
  const [score, setScore] = useState(0);
  const [comment, setComment] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    setRole((localStorage.getItem("user_role") as UserRole | null) ?? null);
  }, []);

  useEffect(() => {
    if (!Number.isFinite(organizerId)) {
      setError("Некорректный ID организатора");
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const [profileRes, eventsRes, reviewsRes] = await Promise.all([
          getOrganizerProfile(organizerId),
          getOrganizerEvents(organizerId),
          getOrganizerReviews(organizerId),
        ]);

        if (!cancelled) {
          setProfile(profileRes.data);
          setEvents(eventsRes.data.results ?? []);
          setReviews(reviewsRes.data.results ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить профиль организатора"
              : "Ошибка соединения с сервером";
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [organizerId]);

  const fullName = profile ? `${profile.first_name} ${profile.last_name}`.trim() : "";
  const initials = profile
    ? getInitials(profile.first_name || profile.username, profile.last_name)
    : "U";
  const trustScore = profile?.avg_trust_score ? Number(profile.avg_trust_score) : NaN;
  const roundedTrust = Number.isFinite(trustScore) ? Math.round(trustScore) : 0;

  const frequentPrizes = useMemo(() => profile?.frequent_prizes ?? [], [profile?.frequent_prizes]);

  async function refreshReviews() {
    const reviewsRes = await getOrganizerReviews(organizerId);
    setReviews(reviewsRes.data.results ?? []);
  }

  async function handleSubmitReview(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!selectedEventId || score < 1) {
      setSubmitError("Выберите мероприятие и оценку");
      return;
    }

    setSubmitError("");
    setSubmitLoading(true);
    try {
      await createReview(organizerId, {
        event: selectedEventId,
        score,
        comment: comment.trim() || undefined,
      });
      setComment("");
      setScore(0);
      setSelectedEventId("");
      await refreshReviews();
      setActiveTab("reviews");
    } catch (err) {
      if (err instanceof AxiosError && err.response?.data) {
        const data = err.response.data as Record<string, unknown>;
        const detail = typeof data.detail === "string" ? data.detail : null;
        setSubmitError(detail ?? "Не удалось отправить отзыв");
      } else {
        setSubmitError("Ошибка соединения с сервером");
      }
    } finally {
      setSubmitLoading(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-neutral-500">Загрузка профиля...</p>;
  }

  if (error || !profile) {
    return <div className="p-3 rounded bg-danger/10 text-danger text-sm">{error || "Профиль не найден"}</div>;
  }

  return (
    <div>
      <section className="card p-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="h-20 w-20 rounded-full bg-brand text-2xl text-white font-semibold flex items-center justify-center shrink-0">
            {initials}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-semibold text-neutral-900">{fullName || "Без имени"}</h1>
              <span className="text-neutral-400">@{profile.username}</span>
              {profile.is_verified ? (
                <span className="badge bg-success/10 text-success">
                  <CheckCircle className="h-3.5 w-3.5 mr-1" />
                  Верифицирован
                </span>
              ) : null}
            </div>

            <div className="mt-2 flex items-center gap-1.5 text-sm text-neutral-500">
              <MapPin className="h-3.5 w-3.5" />
              <span>{profile.city || "Город не указан"}</span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-4">
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{profile.events_count}</p>
                <p className="text-xs text-neutral-500">проведено</p>
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">
                  {Number.isFinite(trustScore) ? trustScore.toFixed(2) : "—"}
                </p>
                <p className="text-xs text-neutral-500">из 5</p>
                <div className="mt-1">
                  <Stars value={roundedTrust} />
                </div>
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{profile.reviews_count}</p>
                <p className="text-xs text-neutral-500">участников</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="card p-4 mb-6">
        <h2 className="text-sm font-medium mb-3 text-neutral-900">Обычно даёт</h2>
        {frequentPrizes.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {frequentPrizes.map((item, idx) => {
              const prizeType = String(item.prize_type ?? item.name ?? "Приз");
              const countValue = item.count;
              const count = typeof countValue === "number" ? ` (${countValue})` : "";
              return (
                <span key={`${prizeType}-${idx}`} className="badge bg-warning/10 text-warning">
                  <Gift className="h-3.5 w-3.5 mr-1" />
                  {prizeType}
                  {count}
                </span>
              );
            })}
          </div>
        ) : (
          <p className="text-neutral-400 text-sm">Информация не добавлена</p>
        )}
      </section>

      <div className="flex items-center gap-6 mb-4">
        <button
          type="button"
          className={`border-b-2 pb-2 text-sm ${
            activeTab === "events" ? "border-brand text-brand" : "border-transparent text-neutral-500"
          }`}
          onClick={() => setActiveTab("events")}
        >
          Мероприятия
        </button>
        <button
          type="button"
          className={`border-b-2 pb-2 text-sm ${
            activeTab === "reviews" ? "border-brand text-brand" : "border-transparent text-neutral-500"
          }`}
          onClick={() => setActiveTab("reviews")}
        >
          Отзывы
        </button>
      </div>

      {activeTab === "events" ? (
        <div>
          {events.length === 0 ? <p className="text-sm text-neutral-500">Мероприятия не найдены.</p> : null}
          {events.map((event) => (
            <article key={event.id} className="card p-4 flex items-center gap-4 mb-2">
              <div className="text-sm text-neutral-400 w-24 shrink-0">{formatDate(event.event_date)}</div>
              <div className="min-w-0 flex-1">
                <p className="font-medium text-neutral-900 truncate">{event.name}</p>
                <span className="badge bg-neutral-100 text-neutral-600 mt-1">{typeLabelMap[event.event_type]}</span>
              </div>
              <div className="text-brand font-medium text-sm shrink-0">{event.base_points} баллов</div>
            </article>
          ))}
        </div>
      ) : (
        <div>
          {reviews.length === 0 ? <p className="text-sm text-neutral-500 mb-4">Отзывов пока нет.</p> : null}
          {reviews.map((review) => (
            <article key={review.id} className="card p-4 mb-2">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="h-8 w-8 rounded-full bg-brand text-white text-xs font-semibold flex items-center justify-center shrink-0">
                    {getInitials(review.reviewer_name || "U", "")}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">{review.reviewer_name}</p>
                    <p className="text-xs text-neutral-400">{formatDate(review.created_at)}</p>
                  </div>
                </div>
                <Stars value={review.score} />
              </div>
              <p className="text-xs text-neutral-400 mt-2">{review.event_name}</p>
              <p className="text-sm text-neutral-700 mt-1">{review.comment}</p>
            </article>
          ))}

          {role === "PARTICIPANT" ? (
            <form onSubmit={handleSubmitReview} className="card p-4 mt-4">
              <h3 className="font-medium text-neutral-900 mb-3">Оставить отзыв</h3>

              <label className="block text-sm text-neutral-700 mb-1" htmlFor="review-event">
                Мероприятие
              </label>
              <select
                id="review-event"
                className="input"
                value={selectedEventId}
                onChange={(e) => setSelectedEventId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">Выберите мероприятие</option>
                {events
                  .filter((event) => event.status === "COMPLETED")
                  .map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.name}
                    </option>
                  ))}
              </select>
              <p className="text-xs text-neutral-400 mt-1">
                Отзыв можно оставить только на завершённое мероприятие, в котором вы подтверждены как участник
              </p>

              <div className="mt-3">
                <p className="text-sm text-neutral-700 mb-1">Оценка</p>
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }, (_, idx) => idx + 1).map((value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setScore(value)}
                      className="p-1 rounded hover:bg-neutral-50"
                    >
                      <Star
                        className={
                          value <= score ? "h-5 w-5 text-yellow-400 fill-yellow-400" : "h-5 w-5 text-neutral-200"
                        }
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-3">
                <label className="block text-sm text-neutral-700 mb-1" htmlFor="review-comment">
                  Комментарий
                </label>
                <textarea
                  id="review-comment"
                  className="input min-h-24 resize-y"
                  placeholder="Комментарий (необязательно)"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
              </div>

              {submitError ? <p className="text-sm text-danger mt-2">{submitError}</p> : null}

              <button type="submit" className="btn-primary mt-4" disabled={submitLoading}>
                {submitLoading ? "Отправка..." : "Отправить"}
              </button>
            </form>
          ) : null}
        </div>
      )}
    </div>
  );
}
