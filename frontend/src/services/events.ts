import api from "@/lib/api";
import { Event, EventParticipant, PaginatedResponse } from "@/types";

// GET /api/events/
export const getEvents = (params?: {
  category?: string;
  status?: string;
  event_type?: string;
  date_from?: string;
  date_to?: string;
  organizer_id?: number;
  page?: number;
  ordering?: string;
}) => api.get<PaginatedResponse<Event>>("/api/events/", { params });

// GET /api/events/{id}/
export const getEvent = (id: number) => api.get<Event>(`/api/events/${id}/`);

// POST /api/events/
export const createEvent = (data: Partial<Event>) =>
  api.post<Event>("/api/events/", data);

// PATCH /api/events/{id}/
export const updateEvent = (id: number, data: Partial<Event>) =>
  api.patch<Event>(`/api/events/${id}/`, data);

// DELETE /api/events/{id}/
export const deleteEvent = (id: number) =>
  api.delete(`/api/events/${id}/`);

// POST /api/events/{id}/register/
export const registerForEvent = (id: number) => api.post(`/api/events/${id}/register/`);

// GET /api/events/{id}/participants/
export const getEventParticipants = (id: number) =>
  api.get<EventParticipant[]>(`/api/events/${id}/participants/`);

// POST /api/events/{id}/confirm/{user_id}/
export const confirmParticipant = (eventId: number, userId: number) =>
  api.post(`/api/events/${eventId}/confirm/${userId}/`);

// GET /api/events/{id}/my-participation/
export const getMyParticipation = (eventId: number) =>
  api.get<import("@/types").Participation>(`/api/events/${eventId}/my-participation/`);

// POST /api/events/{id}/organizer-checkin/
export const organizerCheckin = (eventId: number, qrToken: string) =>
  api.post<import("@/types").EventParticipant>(`/api/events/${eventId}/organizer-checkin/`, { qr_token: qrToken });
