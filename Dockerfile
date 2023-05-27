# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire bot application to the container
COPY . .

# Start server.
EXPOSE 8080

# Specify the command to run the bot script
CMD ["python", "telegram_bot.py"]
