FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port streamlit runs on
EXPOSE 8501

# Command to run the streamlit app
CMD ["streamlit", "run", "app.py"]
