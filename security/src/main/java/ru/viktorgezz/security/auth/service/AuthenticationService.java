package ru.viktorgezz.security.auth.service;


import ru.viktorgezz.security.auth.dto.AuthenticationRequest;
import ru.viktorgezz.security.auth.dto.AuthenticationResponse;
import ru.viktorgezz.security.auth.dto.RefreshRequest;
import ru.viktorgezz.security.auth.dto.RegistrationRequest;
import ru.viktorgezz.security.auth.user.Role;

/**
 * Сервис для аутентификации и регистрации пользователей.
 */
public interface AuthenticationService {

    /**
     * Выполняет аутентификацию пользователя и возвращает токены доступа.
     *
     * @param request запрос с учетными данными пользователя.
     * @return ответ с access и refresh токенами.
     */
    AuthenticationResponse login(AuthenticationRequest request);

    /**
     * Регистрирует нового пользователя в системе.
     *
     * @param request запрос с данными для регистрации.
     * @param role роль пользователя.
     */
    void register(RegistrationRequest request, Role role);

    /**
     * Обновляет access токен с использованием refresh токена.
     *
     * @param request запрос с refresh токеном.
     * @return ответ с новым access токеном.
     * @throws ru.viktorgezz.security.exception.BusinessException если refresh токен недействителен или истек.
     */
    AuthenticationResponse refreshToken(RefreshRequest request);

    /**
     * Выполняет выход пользователя из системы, удаляя refresh токен.
     *
     * @param refreshToken refresh токен для удаления.
     */
    void logout(String refreshToken);
}
