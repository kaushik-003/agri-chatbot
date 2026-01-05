#  official lightweight Python image
FROM python:3.10-slim

# working directory in the container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
# We install standard tools first just in case
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Start the application on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]