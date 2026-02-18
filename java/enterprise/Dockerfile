FROM maven:3.9-eclipse-temurin-17 as builder

WORKDIR /build
COPY . .

RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/target/*-with-dependencies.jar app.jar

EXPOSE 9090

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

ENTRYPOINT ["java"]
CMD ["-jar", "app.jar"]