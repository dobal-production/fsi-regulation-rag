FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

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