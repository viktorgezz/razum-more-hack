package ru.viktorgezz.security.handler;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * DTO ответа об ошибке для REST API.
 */
@Getter
@NoArgsConstructor
public class ErrorResponse {

    private String message;
    private String code;
    private List<ValidationError> validationErrors;

    public ErrorResponse(String message, String code) {
        this.message = message;
        this.code = code;
    }

    public ErrorResponse(List<ValidationError> validationErrors) {
        this.validationErrors = validationErrors;
    }

    @Override
    public String toString() {
        return "ErrorResponse{" +
                "message='" + message + '\'' +
                ", code='" + code + '\'' +
                ", validationErrors=" + validationErrors +
                '}';
    }
}