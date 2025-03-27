# recipe-app-apt
Recipe API project

## Build image
docker build .
docker-compose build

## Create new project
docker-compose run --rm app sh -c "django-admin startproject app ."

## Run app
docker-compose up  

## GitHub Actions
If not logged in, will use up the 100/6h fast shared by all users. If logged in it will
be 200/6h for ourself