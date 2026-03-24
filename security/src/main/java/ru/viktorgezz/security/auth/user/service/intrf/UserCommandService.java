package ru.viktorgezz.security.auth.user.service.intrf;

import ru.viktorgezz.security.auth.user.User;

/**
 * Сервис для управления пользователями (создание, обновление).
 */
public interface UserCommandService {

    void save(User user);
}
