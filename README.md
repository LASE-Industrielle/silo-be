# silo-be

### Dockerized Postgresql DB (server and client), up and running

- Make sure docker deamon is running
- `docker-compose up -d` (d is for detached) should be enough to have postgresql set up. 
- there are two containers, one for postgres DB, and another for pgAdmin.
- If you already have installed postgresql on local machine please
 execute this command: `brew services stop postgresql` 
- execute `mkdir db-data` (in project root directory) to create directory that will be 
used as volume for the DB
- open local pgAdmin (http://localhost:5050), default credentials 
are `pgadmin4@pgadmin.org` and `admin` (see `docker-compose.yml`)
- create DB server, credentials are also in `docker-compose.yml`
    - Note: Instead of `localhost`, provide `postgres` as host name 
    (that's the bridged network connection name between two containers)
- create `db-data` database in pgAdmin
- To stop running docker container images execute: `docker-compose down`
 

### Starting an app for the first time

- Start docker containers with docker-compose (see above)

- `python3 manage.py migrate`
- `python3 manage.py createsuperuser --email admin@admin.com --username admin`
- `python3 manage.py loaddata initial_data.json`
- `python3 manage.py runserver`


### Generating tokens for already created users
- `python3 manage.py drf_create_token <username>`


### Regenerating tokens
- `python3 manage.py drf_create_token -r <username>`


### Error: That port is already in use.
- `sudo lsof -t -i tcp:8000 | xargs kill -9`

### See live logs from heroku app
- `heroku logs --tail`
