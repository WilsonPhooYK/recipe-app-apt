FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="Wilson"

# Copy the default.conf.tpl file to the nginx configuration directory
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
# Copy params file to the nginx configuration directory
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    # Make nginx user nec
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    # Make sure the nginx user can write to the default.conf file
    chmod +x /run.sh


# Default volume vouling to /vol/static
VOLUME /vol/static

USER nginx

CMD ["/run.sh"]
