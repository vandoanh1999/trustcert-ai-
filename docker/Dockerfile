FROM python:3.10-slim

WORKDIR /app

COPY . .

# It's better practice to copy only the requirements file first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

EXPOSE 8000

CMD ["bash", "docker/start.sh"]
