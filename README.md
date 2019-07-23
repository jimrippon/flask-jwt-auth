# Flask JWT Auth

[![Build Status](https://travis-ci.org/realpython/flask-jwt-auth.svg?branch=master)](https://travis-ci.org/realpython/flask-jwt-auth)

## Quick Start

### Basics

1.  Activate a virtualenv
2.  Install the requirements

### Set Environment Variables

Update *project/server/config.py*, and then run:

```
$ export APP_SETTINGS="project.server.config.DevelopmentConfig"
```

or

```
$ export APP_SETTINGS="project.server.config.ProductionConfig"
```

### Create DB

Create the databases in `psql`:

```
$ psql
# create database flask_jwt_auth
# create database flask_jwt_auth_testing
# \q
```

Create the tables and run the migrations:

```
$ python manage.py create_db
$ python manage.py db init
$ python manage.py db migrate
```

### Run the Application

```
$ python manage.py runserver
```

So access the application at the address [http://localhost:5000/](http://localhost:5000/)

> Want to specify a different port?
> 
> ```
> $ python manage.py runserver -h 0.0.0.0 -p 8080
> ```

### Testing

Without coverage:

```
$ python manage.py test
```

With coverage:

```
$ python manage.py cov
```
