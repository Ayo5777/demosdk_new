# Use an official Python runtime as the base image
FROM python:3.9

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y \
    libwebkit2gtk-4.0-dev


# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Railway-specific configuration: specify the port binding

# Expose the port that the FastAPI app will run on
EXPOSE 8000

# Set the command to run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
