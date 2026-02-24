FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the KMS code into a 'kms' subdirectory
# This ensures that 'import kms.xxx' works correctly
COPY . ./kms/

# Set PYTHONPATH to the current workdir
ENV PYTHONPATH=/app
ENV KMS_HISTORY_PATH=/app/history
ENV KMS_RPM=1

# Default port (can be overridden)
ENV KMS_PORT=4001
EXPOSE $KMS_PORT

CMD ["sh", "-c", "uvicorn kms.main:app --host 0.0.0.0 --port $KMS_PORT"]
