FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and set ownership
RUN adduser --disabled-password --gecos "" myuser && \ 
    chown -R myuser:myuser /app

# Copy app code
COPY . .

USER myuser

# Expose the port
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 


