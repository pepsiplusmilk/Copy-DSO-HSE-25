# DFD — Data Flow Diagram

```mermaid
flowchart LR
  %% Внешний мир (интернет)
  U[User]

  %% Зона приложения
  subgraph AppZone[Trust Boundary: Application Zone]
    WA[WebApp]
  end

  %% Зона данных
  subgraph DataZone[Trust Boundary: Data Zone]
    DB[(Database)]
  end

  %% --- Потоки User -> WebApp ---
  %% F1: Регистрация
  U -->|F1: HTTPS<br/>credentials| WA
  %% F3: Аутентификация
  U -->|F3: HTTPS<br/>credentials| WA
  %% F6: Создание доски
  U -->|F6: HTTPS<br/>JWT, board| WA
  %% F8: Голосование
  U -->|F8: HTTPS<br/>JWT, vote| WA
  %% F10: Завершение голосования/закрытие доски
  U -->|F10: HTTPS<br/>JWT, request| WA

  %% --- Потоки WebApp -> User ---
  %% F5: Возврат токена
  WA -.->|F5: HTTPS<br/>JWT| U

  %% --- Потоки WebApp -> Database ---
  %% F2: Создание учетной записи пользователя
  WA -->|F2: DB conn<br/>user| DB
  %% F4: Проверка учетных данных
  WA -->|F4: DB conn<br/>credentials lookup| DB
  %% F7: Запись доски
  WA -->|F7: DB conn<br/>board| DB
  %% F9: Запись голоса
  WA -->|F9: DB conn<br/>vote| DB
  %% F11: Обновление статуса голосования
  WA -->|F11: DB conn<br/>board_status| DB

  linkStyle default font-size: 10px;
```

## Список потоков данных

| ID  | Откуда → Куда     | Канал/протокол                 | Данные/PII         | Комментарий                   |
|-----|-------------------|--------------------------------|--------------------|-------------------------------|
| F1  | User → WebApp     | HTTPS                          | credentials        | Регистрация пользователя      |
| F2  | WebApp → Database | Соединение с БД (драйвер/SSL*) | user               | Создание пользователя в БД    |
| F3  | User → WebApp     | HTTPS                          | credentials        | Аутентификация пользователя   |
| F4  | WebApp → Database | Соединение с БД (драйвер/SSL*) | credentials lookup | Проверка учетных данных в БД  |
| F5  | WebApp → User     | HTTPS                          | JWT                | Возврат JWT-токена            |
| F6  | User → WebApp     | HTTPS (Bearer JWT)             | JWT, board         | Создание доски                |
| F7  | WebApp → Database | Соединение с БД (драйвер/SSL*) | board              | Запись доски в БД             |
| F8  | User → WebApp     | HTTPS (Bearer JWT)             | JWT, vote          | Голосование за идею           |
| F9  | WebApp → Database | Соединение с БД (драйвер/SSL*) | vote               | Запись голоса в БД            |
| F10 | User → WebApp     | HTTPS (Bearer JWT)             | JWT, request       | Запрос на закрытие доски      |
| F11 | WebApp → Database | Соединение с БД (драйвер/SSL*) | board_status       | Обновление статуса доски в БД |
