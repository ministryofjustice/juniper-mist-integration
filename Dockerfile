FROM python:3.11.5

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

# Set the src directory
ENV PYTHONPATH=/app/src

# Run tests when the container launches
CMD ["python", "-m", "unittest", "discover", "-s", "/app", "-t", "/app"]

