FROM python:3.12-slim

# System deps needed by Playwright Chromium in Debian slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 \
    libpangocairo-1.0-0 libpango-1.0-0 \
    libgtk-3-0 \
    fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install browser + any remaining deps Playwright wants
RUN python -m playwright install --with-deps chromium

COPY check_resale.py /app/check_resale.py

# Run once, exit (Railway Cron triggers it)
CMD ["python", "/app/check_resale.py"]