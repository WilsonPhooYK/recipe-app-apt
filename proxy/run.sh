#!/bin/sh

set -e

# Sub in env vars in default.conf.tpl and output to default.conf
envsubst < /etc/nginx/default.conf.tpl > etc/nginx/conf.d/default.conf
# Start nginx in the foreground (daemon off)
# Docker container should run nginx as main the foreground
nginx -g 'daemon off;'