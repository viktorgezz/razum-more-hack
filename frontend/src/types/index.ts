// Аутентификация
export interface TokenPair {
  access: string;
  refresh: string;
}

// Роли
export type UserRole = "ADMIN" | "ORGANIZER" | "PARTICIPANT" | "OBSERVER";

// Категория мероприятия
export interface EventCategory {
  id: number;
  name: string;
  slug: string;
  description: string;
}

// Мероприятие (из openapi схемы Event)
export type EventType = "LECTURE" | "HACKATHON" | "FORUM" | "VOLUNTEER" | "OTHER";
export type EventStatus = "DRAFT" | "PUBLISHED" | "ONGOING" | "COMPLETED" | "CANCELLED";

export interface Prize {
  id: number;
  event: number;
  name: string;
  description: string;
  prize_type: "MERCH" | "TICKETS" | "INTERNSHIP" | "GRANT" | "MEETING";
  quantity: number;
}

export interface Event {
  id: number;
  organizer_id: number;
  category: EventCategory | null;
  category_id?: number | null;
  name: string;
  description: string;
  event_date: string;
  event_type: EventType;
  difficulty_coef: string;
  base_points: number;
  max_participants: number | null;
  status: EventStatus;
  created_at: string;
  prizes: Prize[];
}

// Участие
export interface Participation {
  id: number;
  event: number;
  user: number;
  status: "REGISTERED" | "CHECKED_IN" | "CONFIRMED" | "REJECTED";
  qr_token: string;
  points_awarded: number;
  created_at: string;
}

// Рейтинг
export interface RatingSnapshot {
  id: number;
  user: number;
  username: string;
  first_name: string;
  last_name: string;
  rating_it: string;
  rating_social: string;
  rating_media: string;
  common_rating: string;
  rank: number;
  snapshot_date: string;
}

export interface PointWeight {
  id: number;
  event_type: EventType;
  category: number | null;
  weight: string;
  updated_by: number | null;
  updated_at: string;
}

// Организаторы
export interface OrganizerList {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  avatar: string | null;
  city: string;
  is_verified: boolean;
  events_count: number;
}

export interface OrganizerProfile {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  avatar: string | null;
  city: string;
  is_verified: boolean;
  events_count: number;
  avg_trust_score: string | null; // decimal строка, например "4.50"
  reviews_count: number;
  frequent_prizes: Record<string, unknown>[];
}

export interface OrganizerEvent {
  id: number;
  name: string;
  event_date: string;
  event_type: EventType;
  category: number | null;
  difficulty_coef: string;
  base_points: number;
  status: EventStatus;
}

export interface OrganizerReview {
  id: number;
  organizer: number;
  reviewer: number;
  reviewer_name: string;
  event: number;
  event_name: string;
  score: number;
  comment: string;
  created_at: string;
}

// Кандидаты (инспектор)
export interface CandidateList {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  date_joined: string;
  events_count: number;
  confirmed_count: number;
  total_points: number;
  avg_points: number;
}

// Пагинация
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Админ-панель
export interface PendingOrganizer {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  is_staff: boolean;
}

export interface AdminPointWeight {
  id: number;
  event_type: EventType;
  category: number | null;
  category_name: string | null;
  weight: string;
  updated_by: number | null;
  updated_by_username: string | null;
  updated_at: string;
}

// Участник мероприятия (для организатора)
export interface EventParticipant {
  id: number;
  event_id: number;
  user_id: number;
  username: string;
  first_name: string;
  last_name: string;
  status: "REGISTERED" | "CHECKED_IN" | "CONFIRMED" | "REJECTED";
  qr_token: string;
  checked_in_at: string | null;
  confirmed_at: string | null;
  points_awarded: number;
  created_at: string;
}
