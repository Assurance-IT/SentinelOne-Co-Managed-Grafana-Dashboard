FROM python:alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . fetcher/

# Run project
CMD ["python", "-m", "fetcher"]