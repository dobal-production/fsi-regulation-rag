# musl 기반 Alpine 사용: glibc를 포함하지 않아 glibc 계열 CVE에 노출되지 않음
FROM python:3.12-alpine

WORKDIR /app

RUN apk upgrade --no-cache && apk add --no-cache curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-cache

ENV PATH="/app/.venv/bin:$PATH"

COPY .env .
COPY *.py .
COPY utils/ utils/

# RUN export $(cat .env | xargs)

EXPOSE 80

HEALTHCHECK CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost/_stcore/health')" || exit 1

CMD ["uv", "run", "streamlit", "run", "app.py", \
    "--logger.level", "info", \
    "--browser.gatherUsageStats", "false", \
    "--browser.serverAddress", "0.0.0.0", \
    "--server.enableCORS", "false", \
    "--server.enableXsrfProtection", "false", \
    "--server.baseUrlPath", "/regulation", \
    "--server.port", "80"]