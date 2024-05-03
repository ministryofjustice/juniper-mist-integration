FROM python:3.11.5

# Set the working directory to /app
WORKDIR /app

RUN mkdir /user_session

# Copy the current directory contents into the container at /app
COPY ../backend/src/requirements.txt /tmp/requirements_backend.txt
COPY ../frontend/src/requirements.txt /tmp/requirements_frontend.txt

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
COPY backend/src/ /app/src_backend
COPY frontend/ /app/src_frontend

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ../tmp/requirements_backend.txt
RUN pip install --no-cache-dir -r ../tmp/requirements_frontend.txt

# Set the src directory
ENV PYTHONPATH=/app

# Run tests when the container launches
ENTRYPOINT ["/entrypoint.sh"]

