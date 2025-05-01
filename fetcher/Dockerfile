FROM python:alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY fetchSentinelOne.py .

# Run fetcher directly
CMD ["python", "fetchSentinelOne.py"]