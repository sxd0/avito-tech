# avito-tech

## Реализовано:

- Реализация требований:

  - Авторизация: `/register`, `/login`, `/dummyLogin`
  - CRUD операции с ПВЗ, приёмками и товарами
  - LIFO-удаление товаров
  - Фильтрация и пагинация `/pvz`
  - Интеграционный тест с 50 товарами

- Дополнительные требования:
  - gRPC `/GetPVZList` на порту `3000`
  - Prometheus-метрики (`9000/metrics`) — RPS, время отклика, бизнесовые метрики
  - Логирование действий (`logger.info`)
  - `pytest`, покрытие > 75%
  - Кодогенерация DTO (`generate.py`, swagger.yaml)

## Запуск проекта

### 1. Клонируйте:

```bash
git clone https://github.com/sxd0/avito-tech-main.git
cd avito-tech-main
```

### 2. Создайте `.env`: (Оставил .env-example для упрощенного запуска)

### 3. Поднимите всё:

```bash
docker-compose up --build -d
```

### 4. Выполните миграции:

```bash
docker-compose exec app alembic upgrade head
```

### 5. Запустите тесты:

```bash
docker-compose exec app pytest -v --cov
```

### 6. Метрики:

- [http://localhost:9000/metrics](http://localhost:9000/metrics)

---

## Проверка производительности

### Установка hey (WSL Ubuntu):

```bash
sudo apt update
sudo apt install hey
```

### Пример нагрузки:

```bash
# GET-запрос
hey -z 15s -c 50 http://localhost:8080/api/pvz

# POST с токеном
hey -z 10s -c 10 -m POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <токен>" \
  -d '{"city": "Москва"}' \
  http://localhost:8080/api/pvz
```

---

## Кодогенерация DTO по Swagger

### Установка:

```bash
pip install datamodel-code-generator
```

### Команда генерации:

```bash
datamodel-codegen \
  --input swagger.yaml \
  --input-file-type openapi \
  --output app/schemas/generated.py
```

---

## ✅ Чеклист для ревью:

| Требование                             | Статус      |
| -------------------------------------- | ----------- |
| Все эндпоинты реализованы              | ✅          |
| Приёмка товаров и LIFO                 | ✅          |
| Роли: модератор / сотрудник ПВЗ        | ✅          |
| Авторизация: логин, регистрация, dummy | ✅          |
| Prometheus метрики (9000)              | ✅          |
| Покрытие кода > 75%                    | ✅          |
| Кодогенерация DTO                      | ✅ |
| README, .env.example                   | ✅          |
