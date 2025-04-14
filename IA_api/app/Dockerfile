# Use a base image with CUDA 12.6
FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel


# Create a non-root user
RUN useradd -m -u 1000 user
USER user

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the app
COPY --chown=user . /app

# Expose API port
EXPOSE 7080

# Run the app
CMD ["python3", "-m","uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7080"]
