# Multi-stage build for UMatch Financial Control
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend with Frontend
FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"
ENV PORT="8000"
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
