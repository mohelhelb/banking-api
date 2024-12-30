
# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app/caixa

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose port 5000
EXPOSE 5000

# Execute the start script
CMD ["./start.sh"]
