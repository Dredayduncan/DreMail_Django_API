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
- Throttling (Rate Limiting)

## Prerequisites

- Python 3.x
- Django 3.x
- Django Rest Framework

## Features
- Register a user
- Login
- Logout
- Update Password
- Update User AVI (Profile Picture)
- Search for Users
- Retrieve User Details
- Create Email Group
- Update Email Group Information
- Delete Email Group
- Retrieve Email Details
- Add Users to Email Group
- Remove Users from Email Group
- Retrieve Members of an Email Group
- Search for Email Groups
- Create Drafts
- Delete Drafts
- Update a Draft
- Send Emails to Users
- Retrieve Email Details
- Send Emails to Email Groups
- Set Email Status to Read or Unread
- Filter Emails by Read or Unread
- Retrieve Inbox
- Retrieve Sent Emails
- Retrieve Spam Emails
- Retrieve Junk Emails
- Retrieve Favorite Emails
- Retrieve Trash Emails
- Favorite Emails
- Move Emails to Spam
- Move Emails to Junk
- Move Emails to Trash
- Permanently Delete Emails

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