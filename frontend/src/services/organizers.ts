import api from "@/lib/api";
import {
  OrganizerList,
  OrganizerProfile,
  OrganizerEvent,
  OrganizerReview,
  PaginatedResponse,
} from "@/types";

// GET /api/v1/organizers/
export const getOrganizers = (page?: number) =>
  api.get<PaginatedResponse<OrganizerList>>("/api/v1/organizers/", { params: { page } });

// GET /api/v1/organizers/{id}/
export const getOrganizerProfile = (id: number) =>
  api.get<OrganizerProfile>(`/api/v1/organizers/${id}/`);

// GET /api/v1/organizers/{id}/events/
export const getOrganizerEvents = (id: number, page?: number) =>
  api.get<PaginatedResponse<OrganizerEvent>>(`/api/v1/organizers/${id}/events/`, { params: { page } });

// GET /api/v1/organizers/{id}/reviews/
export const getOrganizerReviews = (id: number, page?: number) =>
  api.get<PaginatedResponse<OrganizerReview>>(`/api/v1/organizers/${id}/reviews/`, {
    params: { page },
  });

// POST /api/v1/organizers/{id}/reviews/create/
export const createReview = (id: number, data: { event: number; score: number; comment?: string }) =>
  api.post<OrganizerReview>(`/api/v1/organizers/${id}/reviews/create/`, data);

// DELETE /api/v1/organizers/{id}/reviews/{review_id}/
export const deleteReview = (organizerId: number, reviewId: number) =>
  api.delete(`/api/v1/organizers/${organizerId}/reviews/${reviewId}/`);
