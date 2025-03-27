# Very stripped and lightweight for docker
FROM python:3.9-alpine3.13
LABEL maintainer="Wilson"

# Dont output python print to console
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# Set value DEV default to false, docker-compose config can change this
ARG DEV=false

# Still need venv as base image dependencies might still clash with proj dependencies
# Upgrade pip for our venv (note the /py/.. is to use the pip inside our venv)
# Install our requirements file
# Remove extra dependencies that no need
# Add user to our image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Default path to /py/bin...
ENV PATH="/py/bin:$PATH"

# Image will run as the last user it swtiched to
USER django-user
