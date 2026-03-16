FROM python:3.12-slim

# Install socat for virtual serial pair creation, plus build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tests

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Test sources are mounted at runtime via docker-compose volume
CMD ["pytest", "integration/", "--junitxml=/results/test-results.xml", "-v"]
