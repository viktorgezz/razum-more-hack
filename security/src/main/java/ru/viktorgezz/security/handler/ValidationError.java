package ru.viktorgezz.security.handler;

import lombok.Getter;
import lombok.Setter;

/**
 * Модель описания ошибки валидации конкретного поля.
 */
@Getter
@Setter
public class ValidationError {

    private String field;
    private String message;

    public ValidationError(String field, String message) {
        this.field = field;
        this.message = message;
    }

    public ValidationError() {
    }

    @Override
    public String toString() {
        return "ValidationError{" +
                "field='" + field + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}