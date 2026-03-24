package ru.viktorgezz.security.auth.controller;

import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import ru.viktorgezz.security.auth.dto.AuthenticationRequest;
import ru.viktorgezz.security.auth.dto.AuthenticationResponse;
import ru.viktorgezz.security.auth.dto.RefreshRequest;
import ru.viktorgezz.security.auth.dto.RegistrationRequest;
import ru.viktorgezz.security.auth.user.Role;
import ru.viktorgezz.security.auth.service.AuthenticationService;

/**
 * REST-контроллер для операций аутентификации пользователей.
 */
@RestController
@RequestMapping("/auth")
public class AuthenticationController {

    private final AuthenticationService authenticationService;

    @Autowired
    public AuthenticationController(AuthenticationService authenticationService) {
        this.authenticationService = authenticationService;
    }

    @PostMapping("/login")
    public AuthenticationResponse login(
            @RequestBody
            @Valid
            final AuthenticationRequest authenticationRequest
    ){
        return authenticationService.login(authenticationRequest);
    }

    @GetMapping("/logout")
    public void logout(final String refreshToken){
        authenticationService.logout(refreshToken);
    }

    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public void register(
            @RequestBody
            @Valid
            final RegistrationRequest request
    ){
        authenticationService.register(request, Role.PARTICIPANT);
    }

    @PostMapping("/refresh")
    public AuthenticationResponse refresh(
            @RequestBody
            @Valid
            final RefreshRequest request
    ){
        return authenticationService.refreshToken(request);
    }
}
