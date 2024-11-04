# Use an official Python image as the base
FROM python:3.11-slim

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install poetry==1.7.1 && \
    poetry config virtualenvs.create false

# Set the working directory
WORKDIR /app

# Install system dependencies for Poetry and Django
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files before copying the entire code for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
ARG APP_VERSION
RUN bash -c \
    "if [ -z ${APP_VERSION+x} ]; then \
    echo 'APP_VERSION not set'; \
    else \
    poetry version $APP_VERSION; \
    fi"

ARG INSTALL_DEV=false
RUN bash -c \
    "if [ $INSTALL_DEV == 'true' ]; then \
    poetry install --no-root; \
    else \
    poetry install --no-root --only main; \
    fi"

# Copy the Django project files into the container
COPY scoremanagementapp/ ./scoremanagementapp/
COPY scores/ ./scores/
COPY manage.py ./
COPY entrypoint.sh ./

# Expose the port the Django app runs on
EXPOSE 8000

# Command to run the Django development server under entrypoint.sh
CMD ["bash", "entrypoint.sh"]
