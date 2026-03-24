package ru.viktorgezz.security.refreshtoken;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class RefreshTokenService {

    private final RefreshTokenRepo refreshTokenRepo;

    @Transactional
    public void dropRefreshToken(String token) {
        refreshTokenRepo.deleteByToken(token);
    }
}
