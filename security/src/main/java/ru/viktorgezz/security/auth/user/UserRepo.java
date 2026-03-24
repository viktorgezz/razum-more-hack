package ru.viktorgezz.security.auth.user;

import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface UserRepo extends CrudRepository<User, Long> {

    Optional<User> findByUsername(String username);
}
