FROM node:24.16.0-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/index.html frontend/vite.config.js ./
COPY frontend/src ./src
COPY frontend/public ./public
# Configuración pública del SDK web. Nunca declarar secretos del servidor aquí.
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
RUN test -n "$VITE_FIREBASE_API_KEY" && test -n "$VITE_FIREBASE_AUTH_DOMAIN" \
    && test -n "$VITE_FIREBASE_PROJECT_ID" && test -n "$VITE_FIREBASE_APP_ID" \
    && npm run build

FROM python:3.14.7-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/backend ATLAS_ENV=production PORT=10000
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY scripts/deploy ./scripts/deploy
COPY deploy/data-release.json ./deploy/data-release.json
RUN python scripts/deploy/data_bundle.py install
COPY backend/app ./backend/app
COPY engine ./engine
COPY ml/status.py ./ml/status.py
COPY data/contracts ./data/contracts
COPY --from=frontend /build/frontend/dist ./frontend/dist
RUN useradd --uid 10001 --no-create-home atlas
USER 10001
EXPOSE 10000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --timeout-keep-alive 5"]
