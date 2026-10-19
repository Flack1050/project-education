FROM python:3.12-slim


WORKDIR /app


RUN groupadd -r appgroup \
    && useradd -r -g appgroup -m appuser


COPY requirements.txt .


RUN pip install \
    --no-cache-dir \
    -r requirements.txt


RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        wget \
    && rm -rf /var/lib/apt/lists/*


COPY --chown=appuser:appgroup app.py .


USER appuser


EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
