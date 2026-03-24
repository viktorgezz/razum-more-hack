import api from "@/lib/api";
import { AdminPointWeight, PaginatedResponse, PendingOrganizer } from "@/types";

// GET /api/admin/organizers/pending/
export const getPendingOrganizers = () =>
  api.get<PaginatedResponse<PendingOrganizer>>("/api/admin/organizers/pending/");

// POST /api/admin/organizers/{user_id}/approve/
export const approveOrganizer = (userId: number) =>
  api.post(`/api/admin/organizers/${userId}/approve/`);

// POST /api/admin/organizers/{user_id}/reject/
export const rejectOrganizer = (userId: number) =>
  api.post(`/api/admin/organizers/${userId}/reject/`);

// GET /api/admin/point-weights/
export const getAdminPointWeights = () =>
  api.get<PaginatedResponse<AdminPointWeight>>("/api/admin/point-weights/");

// PATCH /api/admin/point-weights/{id}/
export const updateAdminPointWeight = (id: number, weight: string) =>
  api.patch<AdminPointWeight>(`/api/admin/point-weights/${id}/`, { weight });

// POST /api/v1/ratings/rebuild/
export const rebuildLeaderboard = () =>
  api.post<{ status: string; message: string }>("/api/v1/ratings/rebuild/");
