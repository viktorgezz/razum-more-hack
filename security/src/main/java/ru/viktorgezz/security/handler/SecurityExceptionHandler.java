package ru.viktorgezz.security.handler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import ru.viktorgezz.security.exception.BusinessException;
import ru.viktorgezz.security.exception.ErrorCode;

import java.util.ArrayList;
import java.util.List;

/**
 * Глобальный обработчик исключений REST-контроллеров приложения.
 */
@RestControllerAdvice
public class SecurityExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(SecurityExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(
            final BusinessException e
    ) {
        final ErrorResponse body = new ErrorResponse(
                e.getMessage(),
                e.getErrorCode().getCode()
        );

        log.debug(e.getMessage(), e);

        return ResponseEntity.status(
                e.getErrorCode().getStatus() != null ?
                        e.getErrorCode().getStatus() : HttpStatus.BAD_REQUEST
        ).body(body);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleMethodArgumentNotValidException(
            final MethodArgumentNotValidException e
    ) {
        final List<ValidationError> errors = new ArrayList<>();
        e.getBindingResult()
                .getAllErrors()
                .forEach(error -> {
                    final String fieldName = ((FieldError) error).getField();
                    final String errorCode = error.getDefaultMessage();
                    errors.add(new ValidationError(
                                    fieldName,
                                    errorCode
                            )
                    );
                });

        final ErrorResponse errorResponse = new ErrorResponse(
                errors
        );

        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(errorResponse);
    }

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleBadCredentialsException(final BadCredentialsException e) {
        log.debug(e.getMessage(), e);
        final ErrorResponse body = new ErrorResponse(
                ErrorCode.BAD_CREDENTIALS.getDefaultMessage(),
                ErrorCode.BAD_CREDENTIALS.getCode()
        );
        return ResponseEntity.status(ErrorCode.BAD_CREDENTIALS.getStatus())
                .body(body);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(
            final Exception e
    ) {
        log.error(e.getMessage(), e);
        final ErrorResponse body = new ErrorResponse(
                ErrorCode.INTERNAL_EXCEPTION.getDefaultMessage(),
                ErrorCode.INTERNAL_EXCEPTION.getCode()
        );
        return ResponseEntity.status(ErrorCode.INTERNAL_EXCEPTION.getStatus())
                .body(body);
    }
}
