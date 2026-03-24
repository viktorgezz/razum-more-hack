package ru.viktorgezz.security.auth.dto;

/**
 * Запрос на обновление access-токена по refresh-токену.
 *
 * @param refreshToken действующий refresh-токен
 */
public record RefreshRequest(
        String refreshToken
) {
}
