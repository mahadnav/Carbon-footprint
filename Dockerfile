FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Heroku assigns a dynamic port via $PORT
ENV PORT=8501

# Expose it
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=$PORT", "--server.enableCORS=false"]
