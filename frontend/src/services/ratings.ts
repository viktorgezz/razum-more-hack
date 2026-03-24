import api from "@/lib/api";
import { RatingSnapshot, PointWeight, PaginatedResponse } from "@/types";

// GET /api/v1/ratings/leaderboard/
export const getLeaderboard = (params?: { category?: "it" | "social" | "media"; page?: number }) =>
  api.get<PaginatedResponse<RatingSnapshot>>("/api/v1/ratings/leaderboard/", { params });

// GET /api/v1/ratings/user/{user_id}/
export const getUserRating = (userId: number) =>
  api.get<RatingSnapshot>(`/api/v1/ratings/user/${userId}/`);

// GET /api/v1/ratings/point-weights/
export const getPointWeights = () =>
  api.get<PaginatedResponse<PointWeight>>("/api/v1/ratings/point-weights/");
