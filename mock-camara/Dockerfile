FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8090

# Reads MOCK_CAMARA_PORT if set, defaults to 8090 to match the rest of the stack
ENV MOCK_CAMARA_PORT=8090

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${MOCK_CAMARA_PORT}"]
