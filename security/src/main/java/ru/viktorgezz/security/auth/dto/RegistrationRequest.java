package ru.viktorgezz.security.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Запрос на регистрацию нового пользователя.
 *
 * @param username имя пользователя
 * @param password пароль пользователя
 * @param confirmPassword повтор пароля для валидации
 */
public record RegistrationRequest(

        @NotBlank(message = "Имя не должно быть пустым")
        @Size(
                min = 2,
                max = 255,
                message = "Минимальная длина имени должна быть 2, а максимальная 255"
        )
        String username,

        @NotBlank(message = "Пароль не должен быть пустым")
        @Size(
                min = 8,
                max = 255,
                message = "Минимальная длина пароля должна быть 8, а максимальная 255")
        String password,

        @NotBlank(message = "Повторный пароль не должен быть пустым")
        @Size(
                min = 8,
                max = 255,
                message = "Минимальная длина повторного пароля должна быть 8, а максимальная 255")
        String confirmPassword
) {
}
