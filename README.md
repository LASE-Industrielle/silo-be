# silo-be

### Posgtresql dockerised useful commands
- Install pgAdmin as a client for accessing db, and create database server inside it, and database with the same name as in docker-compose.yaml file (db-data)
- If you already have installed postgresql on local machine please execute this command: `brew services stop postgresql`
- To run docker-compose file and postgresql database execute this command: `docker-compose up`
- To stop running docker container image execute: `docker-compose down`


### Starting an app in development mode
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser --email admin@admin.com --username admin`
- `python3 manage.py loaddata initial_data.json`
- `python3 manage.py loaddata runserver`


### Generating tokens for already created users
- `python3 manage.py drf_create_token <username>`


### Regenerating tokens
- `python3 manage.py drf_create_token -r <username>`
