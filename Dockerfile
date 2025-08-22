FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .
COPY *.py .
COPY utils/ utils/

# RUN export $(cat .env | xargs)

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost/_stcore/health || exit 1
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:80/regulation/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
    "--logger.level", "info", \
    "--browser.gatherUsageStats", "false", \
    "--browser.serverAddress", "0.0.0.0", \
    "--server.enableCORS", "false", \
    "--server.enableXsrfProtection", "false", \
    "--server.baseUrlPath", "/regulation", \
    "--server.port", "80"]