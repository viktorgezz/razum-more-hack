"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Check, RefreshCw, X } from "lucide-react";

import {
  approveOrganizer,
  getAdminPointWeights,
  getPendingOrganizers,
  rebuildLeaderboard,
  rejectOrganizer,
  updateAdminPointWeight,
} from "@/services/admin";
import { AdminPointWeight, PendingOrganizer, UserRole } from "@/types";
import { cn } from "@/lib/utils";

type Tab = "organizers" | "weights";

const eventTypeLabel: Record<string, string> = {
  LECTURE: "Лекция",
  HACKATHON: "Хакатон",
  FORUM: "Форум",
  VOLUNTEER: "Волонтёрство",
  OTHER: "Другое",
};

export default function AdminPage() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole | null>(null);
  const [tab, setTab] = useState<Tab>("organizers");

  // --- Pending organizers ---
  const [organizers, setOrganizers] = useState<PendingOrganizer[]>([]);
  const [orgLoading, setOrgLoading] = useState(true);
  const [orgError, setOrgError] = useState("");
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // --- Point weights ---
  const [weights, setWeights] = useState<AdminPointWeight[]>([]);
  const [weightsLoading, setWeightsLoading] = useState(true);
  const [weightsError, setWeightsError] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");
  const [saveLoading, setSaveLoading] = useState(false);

  // --- Rebuild ---
  const [rebuildLoading, setRebuildLoading] = useState(false);
  const [rebuildMsg, setRebuildMsg] = useState("");

  useEffect(() => {
    const r = localStorage.getItem("user_role") as UserRole | null;
    setRole(r);
    if (r !== "ADMIN") {
      router.replace("/events");
    }
  }, [router]);

  useEffect(() => {
    if (tab === "organizers") loadOrganizers();
    else loadWeights();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  async function loadOrganizers() {
    setOrgLoading(true);
    setOrgError("");
    try {
      const res = await getPendingOrganizers();
      setOrganizers(res.data.results ?? []);
    } catch (err) {
      setOrgError(
        err instanceof AxiosError && err.response?.status
          ? "Не удалось загрузить список"
          : "Ошибка соединения"
      );
    } finally {
      setOrgLoading(false);
    }
  }

  async function loadWeights() {
    setWeightsLoading(true);
    setWeightsError("");
    try {
      const res = await getAdminPointWeights();
      setWeights(res.data.results ?? []);
    } catch (err) {
      setWeightsError(
        err instanceof AxiosError && err.response?.status
          ? "Не удалось загрузить веса"
          : "Ошибка соединения"
      );
    } finally {
      setWeightsLoading(false);
    }
  }

  async function handleApprove(userId: number) {
    setActionLoading(userId);
    try {
      await approveOrganizer(userId);
      setOrganizers((prev) => prev.filter((o) => o.id !== userId));
    } catch {
      // ignore
    } finally {
      setActionLoading(null);
    }
  }

  async function handleReject(userId: number) {
    setActionLoading(userId);
    try {
      await rejectOrganizer(userId);
      setOrganizers((prev) => prev.filter((o) => o.id !== userId));
    } catch {
      // ignore
    } finally {
      setActionLoading(null);
    }
  }

  async function handleSaveWeight(id: number) {
    setSaveLoading(true);
    try {
      const res = await updateAdminPointWeight(id, editValue);
      setWeights((prev) => prev.map((w) => (w.id === id ? res.data : w)));
      setEditingId(null);
    } catch {
      // ignore
    } finally {
      setSaveLoading(false);
    }
  }

  async function handleRebuild() {
    setRebuildLoading(true);
    setRebuildMsg("");
    try {
      const res = await rebuildLeaderboard();
      setRebuildMsg(res.data.message);
    } catch {
      setRebuildMsg("Ошибка при пересчёте");
    } finally {
      setRebuildLoading(false);
    }
  }

  if (role !== "ADMIN") return null;

  return (
    <div>
      <header className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900">Управление</h1>
          <p className="text-sm text-neutral-500">Административная панель</p>
        </div>
        <button
          type="button"
          className="btn-secondary inline-flex items-center gap-2"
          onClick={handleRebuild}
          disabled={rebuildLoading}
        >
          <RefreshCw className={cn("h-4 w-4", rebuildLoading && "animate-spin")} />
          Пересчитать рейтинг
        </button>
      </header>

      {rebuildMsg ? (
        <div className="mb-4 p-3 rounded bg-success/10 text-success text-sm">{rebuildMsg}</div>
      ) : null}

      <div className="flex items-center gap-6 mb-6 border-b border-neutral-200">
        {(["organizers", "weights"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={cn(
              "pb-3 text-sm border-b-2 transition-colors",
              tab === t
                ? "border-brand text-brand font-medium"
                : "border-transparent text-neutral-500 hover:text-neutral-800"
            )}
          >
            {t === "organizers" ? "Организаторы на модерации" : "Веса баллов"}
          </button>
        ))}
      </div>

      {tab === "organizers" ? (
        <section>
          {orgLoading ? <p className="text-sm text-neutral-500">Загрузка...</p> : null}
          {orgError ? <p className="text-sm text-danger">{orgError}</p> : null}
          {!orgLoading && !orgError && organizers.length === 0 ? (
            <div className="card p-8 text-center text-neutral-500 text-sm">
              Нет организаторов, ожидающих верификации
            </div>
          ) : null}
          {organizers.map((org) => {
            const name = `${org.first_name} ${org.last_name}`.trim() || org.username;
            const isLoading = actionLoading === org.id;
            return (
              <div key={org.id} className="card p-4 mb-2 flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-brand text-white text-sm font-semibold flex items-center justify-center shrink-0">
                  {org.first_name?.[0] ?? org.username[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-neutral-900">{name}</p>
                  <p className="text-xs text-neutral-500">@{org.username} · {org.email}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-success/10 text-success hover:bg-success/20 transition-colors disabled:opacity-50"
                    onClick={() => handleApprove(org.id)}
                    disabled={isLoading}
                  >
                    <Check className="h-4 w-4" />
                    Принять
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-danger/10 text-danger hover:bg-danger/20 transition-colors disabled:opacity-50"
                    onClick={() => handleReject(org.id)}
                    disabled={isLoading}
                  >
                    <X className="h-4 w-4" />
                    Отклонить
                  </button>
                </div>
              </div>
            );
          })}
        </section>
      ) : (
        <section>
          {weightsLoading ? <p className="text-sm text-neutral-500">Загрузка...</p> : null}
          {weightsError ? <p className="text-sm text-danger">{weightsError}</p> : null}
          <div className="card overflow-hidden">
            <div className="text-xs uppercase text-neutral-500 bg-neutral-50 border-b border-neutral-200 grid grid-cols-[2fr_2fr_1.5fr_1.5fr_auto] gap-3 px-4 py-3">
              <span>Тип мероприятия</span>
              <span>Категория</span>
              <span>Вес</span>
              <span>Обновил</span>
              <span />
            </div>
            {weights.map((w) => (
              <div
                key={w.id}
                className="border-b border-neutral-100 grid grid-cols-[2fr_2fr_1.5fr_1.5fr_auto] gap-3 px-4 py-3 items-center text-sm"
              >
                <span className="font-medium text-neutral-900">
                  {eventTypeLabel[w.event_type] ?? w.event_type}
                </span>
                <span className="text-neutral-600">{w.category_name ?? "Все категории"}</span>
                <span>
                  {editingId === w.id ? (
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      className="input w-24 py-1"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      autoFocus
                    />
                  ) : (
                    <span className="font-medium text-brand">{w.weight}</span>
                  )}
                </span>
                <span className="text-neutral-400 text-xs">{w.updated_by_username ?? "—"}</span>
                <span>
                  {editingId === w.id ? (
                    <div className="flex gap-1">
                      <button
                        type="button"
                        className="px-2 py-1 text-xs bg-brand text-white rounded disabled:opacity-50"
                        onClick={() => handleSaveWeight(w.id)}
                        disabled={saveLoading}
                      >
                        Сохранить
                      </button>
                      <button
                        type="button"
                        className="px-2 py-1 text-xs bg-neutral-100 text-neutral-600 rounded"
                        onClick={() => setEditingId(null)}
                      >
                        Отмена
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      className="px-2 py-1 text-xs bg-neutral-100 text-neutral-600 rounded hover:bg-neutral-200"
                      onClick={() => { setEditingId(w.id); setEditValue(w.weight); }}
                    >
                      Изменить
                    </button>
                  )}
                </span>
              </div>
            ))}
            {!weightsLoading && weights.length === 0 ? (
              <p className="px-4 py-6 text-sm text-neutral-500">Веса не настроены</p>
            ) : null}
          </div>
        </section>
      )}
    </div>
  );
}
