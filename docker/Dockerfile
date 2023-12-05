FROM python:3.11.5

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ../src/requirements.txt /tmp/requirements.txt

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
COPY src/ /app/src

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ../tmp/requirements.txt

# Set the src directory
ENV PYTHONPATH=/app/src

# Run tests when the container launches
ENTRYPOINT ["/entrypoint.sh"]

