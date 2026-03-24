package ru.viktorgezz.security.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

/**
 * Перечень кодов и шаблонов сообщений ошибок бизнес-логики.
 */
@RequiredArgsConstructor
@Getter
public enum ErrorCode {

    USER_NOT_FOUND("User not found", "User with username: %s - not found", HttpStatus.NOT_FOUND),
    PASSWORD_MISMATCH("PASSWORD_MISMATCH", "Current password and new password are not the same", HttpStatus.BAD_REQUEST),
    BAD_CREDENTIALS("BAD_CREDENTIALS", "Username and / or password is incorrect", HttpStatus.UNAUTHORIZED),
    TOKEN_REFRESH_EXPIRED("UNAUTHORIZED", "JWT token is expired", HttpStatus.UNAUTHORIZED),
    USER_FORBIDDEN("Forbidden", "User with id: %s is not authorized to access this resource", HttpStatus.FORBIDDEN),
    INTERNAL_EXCEPTION("INTERNAL_EXCEPTION", "Internal error", HttpStatus.INTERNAL_SERVER_ERROR);

    private final String code;
    private final String defaultMessage;
    private final HttpStatus status;
}
