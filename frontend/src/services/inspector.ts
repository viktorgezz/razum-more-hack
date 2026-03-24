import api from "@/lib/api";
import { CandidateList, PaginatedResponse } from "@/types";

// GET /api/inspector/candidates/
export const getCandidates = (params?: {
  min_avg_points?: number;
  max_avg_points?: number;
  min_events?: number;
  max_events?: number;
  ordering?: string; // total_points, avg_points, events_count, date_joined (и с -)
  page?: number;
}) => api.get<PaginatedResponse<CandidateList>>("/api/inspector/candidates/", { params });

// GET /api/inspector/candidates/{user_id}/report/ — скачать PDF
export const getCandidateReportUrl = (userId: number) =>
  `${process.env.NEXT_PUBLIC_API_URL}/api/inspector/candidates/${userId}/report/`;
