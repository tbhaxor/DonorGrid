# DonorGrid Deployment Guide

In this deployment guide you will learn the methods to deploy and debug the application. The easiest way recommended is to use docker-compose.

In production environment, the application requires postgres database

## Environment Variables

The application let you choose what your postgres connection, and the app level configuration.

|Env Name|Default|Description
|:---:|:---:|:---|
|SECRET|_random string created on runtime_|The django's secret value|
|PY_ENV|prod|This is application environment. Use `dev` for testing|
|DB_NAME|donorgrid|Name of the database|
|DB_HOST|db|Host name of the database server|
|DB_CONN_AGE|None|The lifetime of a database connection|
|DB_PASSWORD|donorgrid|Password of the database user|
|DB_PORT|5432|Port on which postgres is running|
|DB_USER|donorgrid|Username of the database|
|BASE_URL|http://localhost:8000|FQDN base url of the website| 
|POST_DONATION_REDIRECT|Value of `BASE_URL` environment variable|URL to redirect to after executing the donation payments|

## Docker Compose (recommended)

To deploy on the docker you must have following requirements

1. docker runtime
2. docker compose


The steps of deployment are as follows

1. Clone the repository on your server

    ```shell
    git clone https://github.com/donorgrid/DonorGrid && cd DonorGrid
    ```
   
2. Start the application
   ```shell
   docker-compose up -d
   ```

3. Proxy pass http://127.0.0.1:8000 via nginx or apache server with ssl certificates as per your needs. 

### Configuring initial superuser configuration

By default, it will create superuser for admin panel with **donorgrid:donorgrid** credentials. However, you can change this and use your own credentials by setting up the following environment variable for `app` service in _docker-compose.yaml_

|Env Name|Description|
|:---:|:---|
|DG_USER|Username of the donorgrid admin panel|
|DG_PASS|Password of the donorgrid admin panel|
|DG_EMAIL|Email address of the donorgrid admin user|

## Manual Deployment

In case you want to set up your own docker deployment, you can pull official docker images from here &rArr; https://hub.docker.com/r/tbhaxor/donorgrid

You must have following dependencies fulfilled

1. git
2. python >= 3.6 
3. pip >= 21
4. postgresql 13.x
5. ubuntu / debian
6. docker runtime (optional)

The steps of deployment are as follows

1. Clone the repository
   ```shell
   git clone https://github.com/donorgrid/DonorGrid.git /opt/donorgrid
   ```
   
2. Install pip packages
   ```shell
   pip install -r /opt/donorgrid/requirements.txt
   ```

3. Configure your environment variables as described above and add export them in your .bashrc file
   
4. Source .bashrc file
   ```shell
   source ~/.bashrc
   ```
   
5. Run DB migrations
   ```shell
   cd /opt/donorgrid && python manage.py migrate
   ```
   
   **Note** The command will only fail in case of wrong DB configurations
6. Create a super user for the application
   ```shell
   python manage.py createsuperuser
   ```
   
   **Note** This should be done for the first time only
   
7. Configure app with uwsgi and serve it with apache or nginx (your choice)
