package ru.viktorgezz.security.jwt;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Свойства JWT, считываются из application.yml (security.jwt).
 */
@Component
@ConfigurationProperties(prefix = "security.jwt")
@Getter
@Setter
public class JwtProperties {

    private long accessExpirationMs;

    private long refreshExpirationMs;

}
