# Flask JWT Auth

[![Build Status](https://travis-ci.org/jimrippon/flask-jwt-auth.svg?branch=jwt-auth)](https://travis-ci.org/jimrippon/flask-jwt-auth)[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1f487840dab140b1a36a6682bc48b8e0)](https://www.codacy.com/app/jimrippon/flask-jwt-auth?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jimrippon/flask-jwt-auth&amp;utm_campaign=Badge_Grade)

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
