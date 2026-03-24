FROM maven:3.9.9-eclipse-temurin-21 AS builder
WORKDIR /app

COPY pom.xml .

RUN mvn dependency:go-offline

COPY src ./src

RUN mvn clean install -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app

RUN addgroup --system springgroup && adduser --system springuser --ingroup springgroup

COPY --from=builder --chown=springuser:springgroup --chmod=0550 /app/target/security-0.0.1-SNAPSHOT.jar ./app.jar

USER springuser

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]