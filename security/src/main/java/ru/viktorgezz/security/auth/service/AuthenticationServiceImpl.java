package ru.viktorgezz.security.auth.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import ru.viktorgezz.security.auth.dto.AuthenticationRequest;
import ru.viktorgezz.security.auth.dto.AuthenticationResponse;
import ru.viktorgezz.security.auth.dto.RefreshRequest;
import ru.viktorgezz.security.auth.dto.RegistrationRequest;
import ru.viktorgezz.security.auth.user.Role;
import ru.viktorgezz.security.auth.user.User;
import ru.viktorgezz.security.auth.user.service.intrf.UserCommandService;
import ru.viktorgezz.security.exception.BusinessException;
import ru.viktorgezz.security.exception.ErrorCode;
import ru.viktorgezz.security.exception.InvalidJwtTokenException;
import ru.viktorgezz.security.exception.TokenExpiredException;
import ru.viktorgezz.security.jwt.JwtService;
import ru.viktorgezz.security.refreshtoken.RefreshTokenService;

/**
 * Сервис аутентификации пользователей. Реализует {@link AuthenticationService}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class AuthenticationServiceImpl implements AuthenticationService {

    private final AuthenticationManager authenticationManager;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final RefreshTokenService refreshTokenService;
    private final UserCommandService userCommandService;

    @Override
    public AuthenticationResponse login(AuthenticationRequest authRq) {
        final Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        authRq.name(),
                        authRq.password()
                )
        );

        final User user = (User) authentication.getPrincipal();
        final String accessToken = jwtService.generateAccessToken(user);
        final String refreshToken = jwtService.generateRefreshToken(user);
        final String tokenType = "Bearer";

        return new AuthenticationResponse(
                accessToken,
                refreshToken,
                tokenType
        );
    }

    @Override
    @Transactional
    public void register(RegistrationRequest request, Role role) {
        checkPasswords(request.password(), request.confirmPassword());
        User user = new User(
                request.username(),
                passwordEncoder.encode(request.password()),
                role
        );
        user.setEnabled(true);
        userCommandService.save(user);
        log.debug("Registering user: {}", user);
    }

    @Override
    public AuthenticationResponse refreshToken(RefreshRequest request) {
        try {
            final String accessNewToken = jwtService.refreshToken(request.refreshToken());
            final String tokenType = "Bearer";

            return new AuthenticationResponse(
                    accessNewToken,
                    request.refreshToken(),
                    tokenType
            );
        } catch (InvalidJwtTokenException | TokenExpiredException e) {
            log.debug("Refresh token expired/invalid: {}", e.getMessage());
            throw new BusinessException(ErrorCode.TOKEN_REFRESH_EXPIRED);
        }
    }

    @Override
    @Transactional
    public void logout(String refreshToken) {
        refreshTokenService.dropRefreshToken(refreshToken);
    }

    private void checkPasswords(String password, String confirmPassword) {
        if (password == null || !password.equals(confirmPassword)) {
            throw new BusinessException(ErrorCode.PASSWORD_MISMATCH);
        }
    }
}
