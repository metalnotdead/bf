# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python code into the container
COPY . .

# Expose the port on which your Dash app will run (default is 8050)
EXPOSE 8050

# Set the command to run your Dash app when the container starts
CMD ["python", "stock_forecast.py"]

