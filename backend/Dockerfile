FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Create non-root user
RUN adduser --disabled-password --gecos '' myuser

# Change ownership of /app to myuser
RUN chown -R myuser:myuser /app

USER myuser

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
