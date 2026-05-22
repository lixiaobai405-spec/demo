FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF export (wkhtmltopdf + CJK fonts)
RUN apt-get update \
    && apt-get install -y --no-install-recommends wkhtmltopdf fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Install only production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Copy source code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
