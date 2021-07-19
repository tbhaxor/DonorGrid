# DonorGrid Deployment Guide

In this deployment guide you will learn the methods to deploy and debug the application. The easiest way recommended is to use docker-compose.

In production environment, the application requires postgres database

## Environment Variables

The application let you choose what your postgres connection, and the app level configuration.

|Env Name|Default|Description
|:---:|:---:|:---|
|SECRET|_random string created on runtime_|The django's secret value|
|PY_ENV|prod|The details of |
|DB_NAME|donorgrid|Name of the database|
|DB_HOST|db|Host name of the database server|
|DB_CONN_AGE|None|The lifetime of a database connection|
|DB_PASSWORD|donorgrid|Password of the database user|
|DB_PORT|5432|Port on which postgres is running|
|DB_USER|donorgrid|Username of the database|
|BASE_URL|http://localhost:8000|FQDN base url of the website| 

## Docker Compose (recommended)

To deploy on the docker you must have following requirements

1. docker runtime
2. docker compose

The steps of deployment are as follows

1. Clone the repository on your server

    ```shell
    git clone https://github.com/donorgrid/DonorGrid
    ```
   
2. Configure `server_name` in _nginx.conf_ file
   ```diff
   - server_name _;
   + server_name donation.site.com;
   ```
   
3. Configure nginx port in _docker-compose.yaml_ file
   ```diff
   - - 8080:80
   + 80:80
   ```

4. Boot up the server
   
   ```shell
   docker-compose up 
   ```
   
   **Note** Use `-d` flag to everything in the background

## Manual Deployment

You must have following dependencies fulfilled

1. git
2. python >= 3.6 
3. pip >= 21
4. postgresql 13.x
5. ubuntu / debian

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
4. Run DB migrations
   ```shell
   cd /opt/donorgrid && python manage.py migrate
   ```
   
   **Note** The command will only fail in case of wrong DB configurations
5. Create a super user for the application
   ```shell
   python manage.py createsuperuser
   ```
   
   **Note** This should be done for the first time only
   
6. Configure app with uwsgi and serve it with apache or nginx (your choice)
