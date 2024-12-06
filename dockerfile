# Use a Python base image
FROM python:3.11.1

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first for caching
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project to the working directory
COPY . /app/

# Expose the Django default port
EXPOSE 4100

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start the Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:4100"]