"use client";

import { useEffect, useMemo, useState } from "react";
import { Code, Crown, Heart, Trophy, Tv } from "lucide-react";
import { AxiosError } from "axios";

import { getLeaderboard } from "@/services/ratings";
import { RatingSnapshot } from "@/types";
import { cn, formatRating, getInitials } from "@/lib/utils";

type LeaderboardCategory = "common" | "it" | "social" | "media";

type CategoryCard = {
  key: LeaderboardCategory;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  fieldLabel: string;
};

const categoryCards: CategoryCard[] = [
  { key: "common", title: "Общий", icon: Trophy, fieldLabel: "common_rating" },
  { key: "it", title: "IT", icon: Code, fieldLabel: "rating_it" },
  { key: "social", title: "Соц.", icon: Heart, fieldLabel: "rating_social" },
  { key: "media", title: "Медиа", icon: Tv, fieldLabel: "rating_media" },
];

function getCategoryParams(category: LeaderboardCategory) {
  if (category === "common") return undefined;
  return { category };
}

function getDisplayedRating(user: RatingSnapshot, category: LeaderboardCategory) {
  if (category === "it") return user.rating_it;
  if (category === "social") return user.rating_social;
  if (category === "media") return user.rating_media;
  return user.common_rating;
}

function PodiumCard({
  user,
  place,
}: {
  user: RatingSnapshot;
  place: 1 | 2 | 3;
}) {
  const cardClass =
    place === 1
      ? "bg-yellow-50 border-yellow-200"
      : place === 2
        ? "bg-neutral-50 border-neutral-200"
        : "bg-orange-50 border-orange-100";
  const badgeClass = place === 1 ? "bg-yellow-100 text-yellow-700" : "bg-neutral-100 text-neutral-600";

  return (
    <article className={cn("card flex-1 p-4", cardClass)}>
      <div className="flex items-center justify-between mb-3">
        {place === 1 ? <Crown className="h-5 w-5 text-yellow-500" /> : <span />}
        <span className={cn("badge", badgeClass)}>#{place}</span>
      </div>

      <div className="h-12 w-12 rounded-full bg-brand text-white text-sm font-semibold flex items-center justify-center">
        {getInitials(user.first_name, user.last_name) || getInitials(user.username, "")}
      </div>

      <p className="mt-3 text-sm font-medium text-neutral-900 truncate">
        {[user.first_name, user.last_name].filter(Boolean).join(" ") || "Без имени"}
      </p>
      <p className="text-xs text-neutral-500 truncate">@{user.username}</p>
      <p className="mt-2 text-lg font-semibold text-neutral-900">{formatRating(user.common_rating)}</p>
    </article>
  );
}

export default function LeaderboardPage() {
  const [category, setCategory] = useState<LeaderboardCategory>("common");
  const [leaders, setLeaders] = useState<RatingSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  useEffect(() => {
    const storedUserId = localStorage.getItem("user_id");
    if (!storedUserId) {
      setCurrentUserId(null);
      return;
    }
    const parsed = Number(storedUserId);
    setCurrentUserId(Number.isNaN(parsed) ? null : parsed);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function fetchLeaderboard() {
      setLoading(true);
      setError("");
      try {
        const res = await getLeaderboard(getCategoryParams(category));
        if (!cancelled) {
          setLeaders(res.data.results ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof AxiosError && err.response?.status
              ? "Не удалось загрузить таблицу лидеров"
              : "Ошибка соединения с сервером";
          setError(message);
          setLeaders([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void fetchLeaderboard();

    return () => {
      cancelled = true;
    };
  }, [category]);

  const topThree = leaders.slice(0, 3);
  const rest = leaders.slice(3);

  const selectedField = useMemo(
    () => categoryCards.find((item) => item.key === category)?.fieldLabel ?? "common_rating",
    [category]
  );

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Таблица лидеров</h1>
        <p className="text-sm text-neutral-500">Топ-100 участников</p>
      </header>

      <section className="grid grid-cols-4 gap-3 mb-6">
        {categoryCards.map((item) => {
          const Icon = item.icon;
          const isActive = item.key === category;

          return (
            <button
              key={item.key}
              type="button"
              onClick={() => setCategory(item.key)}
              className={cn(
                "card p-4 cursor-pointer transition-all text-left",
                isActive ? "border-brand bg-brand-light shadow-none" : "hover:shadow-card-hover"
              )}
            >
              <div className="flex items-center justify-between">
                <Icon className={cn("h-4 w-4", isActive ? "text-brand" : "text-neutral-500")} />
                <span className="text-xs text-neutral-400">{item.fieldLabel}</span>
              </div>
              <p className="mt-3 font-medium text-sm text-neutral-900">{item.title}</p>
            </button>
          );
        })}
      </section>

      {loading ? <p className="text-sm text-neutral-500">Загрузка рейтинга...</p> : null}
      {error ? <div className="p-3 rounded bg-danger/10 text-danger text-sm mb-4">{error}</div> : null}

      {!loading && !error ? (
        <>
          <section className="flex gap-4 mb-6">
            {topThree[0] ? <PodiumCard user={topThree[0]} place={1} /> : null}
            {topThree[1] ? <PodiumCard user={topThree[1]} place={2} /> : null}
            {topThree[2] ? <PodiumCard user={topThree[2]} place={3} /> : null}
          </section>

          <section className="card mt-4 overflow-hidden">
            <div className="bg-neutral-50 border-b border-neutral-200 text-xs text-neutral-500 uppercase tracking-wide px-4 py-3 grid grid-cols-[40px_1.6fr_1fr_1fr_1fr_1fr] gap-3">
              <span>#</span>
              <span>Участник</span>
              <span className="text-right">Рейтинг IT</span>
              <span className="text-right">Соц.</span>
              <span className="text-right">Медиа</span>
              <span className="text-right">Общий</span>
            </div>

            {rest.map((user) => {
              const isCurrentUser = currentUserId !== null && user.user === currentUserId;
              const displayName = [user.first_name, user.last_name].filter(Boolean).join(" ") || "Без имени";

              return (
                <div
                  key={user.id}
                  className={cn(
                    "border-b border-neutral-100 hover:bg-neutral-50/50 transition-colors px-4 py-3 grid grid-cols-[40px_1.6fr_1fr_1fr_1fr_1fr] gap-3 items-center",
                    isCurrentUser && "bg-brand/5"
                  )}
                >
                  <span className="text-neutral-400 w-8">{user.rank}</span>

                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="h-8 w-8 rounded-full bg-brand text-white text-xs font-semibold flex items-center justify-center shrink-0">
                      {getInitials(user.first_name, user.last_name) || getInitials(user.username, "")}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-neutral-900 truncate">{displayName}</p>
                      <p className="text-xs text-neutral-500 truncate">@{user.username}</p>
                    </div>
                  </div>

                  <span className="text-sm text-right tabular-nums">{formatRating(user.rating_it)}</span>
                  <span className="text-sm text-right tabular-nums">{formatRating(user.rating_social)}</span>
                  <span className="text-sm text-right tabular-nums">{formatRating(user.rating_media)}</span>
                  <span className="text-sm text-right tabular-nums font-medium">
                    {formatRating(getDisplayedRating(user, category))}
                  </span>
                </div>
              );
            })}
          </section>
        </>
      ) : null}
    </div>
  );
}
