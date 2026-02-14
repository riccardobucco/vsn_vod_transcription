FROM python:3.13-slim

WORKDIR /opt/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Tailwind CSS build
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy and install Node dependencies (Tailwind)
COPY package.json tailwind.config.js ./
RUN npm install

# Copy application code
COPY app/ app/
COPY migrations/ migrations/
COPY alembic.ini ./
COPY worker/ worker/

# Build Tailwind CSS
RUN npx tailwindcss -i app/static/app.css -o app/static/tailwind.css --minify

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
