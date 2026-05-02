FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create a working directory
WORKDIR /app


# Install any dependencies
RUN pip install --upgrade pip
RUN apt-get update \
    && apt-get -y install libpq-dev gcc gdal-bin

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Run the application when the container starts
#CMD ["python", "/app/fetch_court_data.py"]
#CMD ["python", "/app/fetch.py"]
RUN chmod +x /app/court_records/entry_point.sh 

CMD ["/app/court_records/entry_point.sh"]
