# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Создаём пользователя ЗАРАНЕЕ
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

WORKDIR /app

# Копируем зависимости в /usr/local (доступно всем, включая appuser)
COPY --from=builder /root/.local /usr/local

# Устанавливаем wget для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# Копируем код с правами appuser
COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
