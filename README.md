# async-payment-service

REST API сервис для создания и обработки платежей с асинхронной архитектурой.

## Описание

Сервис принимает запрос на создание платежа и обрабатывает его асинхронно.  
После обработки отправляется webhook уведомление с retry-механизмом.  
При невозможности доставки webhook сообщение попадает в DLQ.

## Основные возможности

- Создание платежа (POST /api/v1/payments)
- Получение платежа (GET /api/v1/payments/{id})
- Idempotency через Idempotency-Key
- Асинхронная обработка платежей
- Outbox pattern
- RabbitMQ для обработки событий
- Webhook уведомления
- Retry с exponential backoff
- Dead Letter Queue (DLQ)
- Тесты на pytest

---

## Архитектура

Client → FastAPI → PostgreSQL → Outbox → Publisher → RabbitMQ → Consumer → Webhook

---

## Стек

- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- RabbitMQ
- httpx
- pytest
- Alembic
- Docker / Docker Compose

---

## Запуск

### 1. Клонировать проект

```bash
git clone https://github.com/ratmiryusupov/async-payment-service
cd async-payment-service
```

### 2. Настроить переменные окружения

В репозитории уже есть готовый файл `.env.docker`, который используется для запуска через Docker Compose.

При необходимости вы можете отредактировать значения в этом файле под свою конфигурацию.

Также доступен шаблон `.env.example`, который можно использовать как ориентир:

```bash
cp .env.example .env.docker
```


При необходимости отредактируйте значения.

### 3. Запуск через Docker

```bash
docker compose up --build -d
```

Сервисы:

API: http://localhost:8000

Swagger: http://localhost:8000/docs

RabbitMQ UI: http://localhost:15672

### Тесты

#### Запуск через Docker

```bash
docker compose exec api pytest -v
```

### Примеры запросов

## Создание платежа

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: supersecretkey" \
  -H "Idempotency-Key: test-1" \
  -d '{
    "amount": "100.00",
    "currency": "USD",
    "description": "Test payment",
    "metadata": {"order_id": "42"},
    "webhook_url": "http://127.0.0.1:8000/test-webhook"
  }'
```

## Получение платежа

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/{payment_id}" \
  -H "X-API-Key: supersecretkey"
```


## Idempotency

Если отправить один и тот же запрос с одинаковым `Idempotency-Key`, новый платёж не создастся — сервис просто вернёт уже существующий.  


---

## Webhook

После обработки платежа сервис отправляет POST-запрос на указанный `webhook_url` с результатом операции.

Пример payload:

```json
{
  "payment_id": "...",
  "status": "succeeded",
  "amount": "100.00",
  "currency": "USD",
  "metadata": {...}
}
```

## Retry и DLQ

Если webhook не удалось отправить с первого раза, сервис делает до 3 попыток с увеличивающейся задержкой:

первая попытка — сразу
затем через 1 секунду
затем через 2 секунды
затем через 4 секунды

Если после этого webhook так и не доставлен, сообщение отправляется в очередь payments.dlq для дальнейшего разбора.