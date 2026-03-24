package ru.viktorgezz.security.auth.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Ответ на аутентификацию/обновление токена.
 *
 * @param accessToken выданный access-токен
 * @param refreshToken выданный либо ранее выданный refresh-токен
 * @param tokenType тип токена (обычно "Bearer")
 */
public record AuthenticationResponse(
        @JsonProperty("access_token")
        String accessToken,

        @JsonProperty("refresh_token")
        String refreshToken,

        @JsonProperty("token_type")
        String tokenType
) {
}
