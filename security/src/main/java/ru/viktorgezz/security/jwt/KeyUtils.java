package ru.viktorgezz.security.jwt;

import ru.viktorgezz.security.exception.KeyPemException;

import java.io.IOException;
import java.io.InputStream;
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

/**
 * Утилитный класс для загрузки RSA-ключей из ресурсов.
 */
public class KeyUtils {

    private KeyUtils() {}

    public static PrivateKey loadPrivateKey(final String pemPath)  {
        try {
            final String key = readKeyFromResource(pemPath).replace("-----BEGIN PRIVATE KEY-----","")
                    .replace("-----END PRIVATE KEY-----", "")
                    .replaceAll("\\s+","");
            final byte[] decoded = Base64.getDecoder().decode(key);
            final PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(decoded);
            return KeyFactory.getInstance("RSA").generatePrivate(keySpec);
        } catch (IOException | InvalidKeySpecException | NoSuchAlgorithmException e) {
            throw new KeyPemException(e.getMessage());
        }
    }

    public static PublicKey loadPublicKey(final String pemPath)  {
        try {
            final String key = readKeyFromResource(pemPath).replace("-----BEGIN PUBLIC KEY-----","")
                    .replace("-----END PUBLIC KEY-----", "")
                    .replaceAll("\\s+","");
            final byte[] decoded = Base64.getDecoder().decode(key);
            final X509EncodedKeySpec keySpec = new X509EncodedKeySpec(decoded);
            return KeyFactory.getInstance("RSA").generatePublic(keySpec);
        } catch (IOException | InvalidKeySpecException | NoSuchAlgorithmException e) {
            throw new KeyPemException(e.getMessage());
        }
    }

    private static String readKeyFromResource(String pemPath) throws IOException {
        try (final InputStream inputStream = KeyUtils.class.getClassLoader().getResourceAsStream(pemPath)) {
            if (inputStream == null) {
                throw new IllegalArgumentException("file not found: " + pemPath);
            }
            return new String(inputStream.readAllBytes());
        }
    }
}
