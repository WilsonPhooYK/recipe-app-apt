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
    # Install persist postgreql-client
    # The command apk add is used in Alpine Linux, a lightweight distribution, to install packages (software) from the system’s package repository.
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # Group it so can delete later
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    # -p creates all the subdirectory for the media path
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # Change owner recursive /vol to django-user and group django-user
    chown -R django-user:django-user /vol && \
    # Change permission on that directory, owner and group of that directory can make any changes
    chmod -R 755 /vol

# Default path to /py/bin...
ENV PATH="/py/bin:$PATH"

# Image will run as the last user it swtiched to
USER django-user
