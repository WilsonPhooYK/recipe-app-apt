server {
    # Port server is listening on
    listen ${LISTEN_PORT};

    # Map urls /static/* to /vol/static*
    location /static {
        alias /vol/static;
    }

    # The rest of the requests
    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        # Required for http request to process for uwsgi
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}