# recipe-app-apt
Recipe API project

## Linting
Install pylance, pylint

## Fix pylance issue (Do this for intellisense locally)
After app/app folder structure is up:
python -m venv ./venv
.\venv\Scripts\Activate.ps1
source venv/bin/activate - mac

J:\projects\recipe-app-apt\venv\Scripts\python.exe -m pip install --upgrade pip
pip install -r requirements.txt

## Build image
(No need this) docker build .
docker-compose build

## Create new project
docker-compose run --rm app sh -c "django-admin startproject app ."

## Run app
docker-compose up

## Docker compose down
docker-compose down
The docker-compose down command is used to stop and remove all the containers, networks, volumes, and images associated with a Docker Compose application.

## Swagger
http://localhost:8000/api/docs/

## GitHub Actions
If not logged in, will use up the 100/6h fast shared by all users. If logged in it will
be 200/6h for ourself

## Django test framework
- Test client - dummy web browser
- Simulate authentication
- Temporary database
- API test client

docker-compose run --rm app sh -c "python manage.py test"

## Add new core app
This creates another library app that can be added into the main app
docker-compose run --rm app sh -c "python manage.py startapp core"

## Check db status
docker-compose run --rm app sh -c "python manage.py wait_for_db"

## Migrations
docker-compose run --rm app sh -c "python manage.py makemigrations"
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"

## If volume error
docker volume ls
docker compose down
docker volume rm recipe-app-apt_dev-db-data

## Create superuser
docker-compose run --rm app sh -c "python manage.py createsuperuser"
email@example.com
password

### Authorize in swagger
Token {{token}}

## Collect Static
docker-compose run --rm app sh -c "python manage.py collectstatic"
Puts all static files into STATIC_ROOT