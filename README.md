# Django Email Management System API

## Introduction

This Django API allows you to manage your email with features such as authentication, pagination, and functionalities such as registering a user, user login, getting inbox, sending an email, getting details of a particular email, deleting an email and more. The database for this API is Postgres.
### [The Database Development Process](https://github.com/Dredayduncan/Email-Database)

## Base URL
<not_set>

## Postman Documentation
<not_set>

## Included API Attributes
- JWT Authentication
- Result Pagination
- Versioning

## Prerequisites

- Python 3.x
- Django 3.x
- Django Rest Framework


## Installation

1. Clone the repository:
```
git clone https://github.com/Dredayduncan/DreMail_Django_API.git
```
2. Change into the project directory:
```
cd DreMail_Django_API
```
3. Create your virtual environment
```
python3 -m venv "my_env_name"
```
4. Activate your virtual environment
```
source <env_name>/bin/activate
```
5. Install the required packages:
```
pip install -r requirements.txt
```
6. Migrate the database:
```
python3 manage.py makemigrations
```
```
python3 manage.py migrate
```
7. Run the development server:
```
python3 manage.py runserver
```