# Base image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    libmariadb-dev-compat \
    gcc \
    pkg-config \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/
# Install Python dependencies
RUN apt-get update && apt-get install -y libpq-dev  # 필요한 경우 PostgreSQL 관련 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/
COPY .env /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=2", "--timeout","90"]

