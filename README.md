# Airport API

API service for airport management written on DRF

## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing orders and tickets
* Managing airplane fleets and routes
* Adding flights and flight sessions
* Filtering flights and airports

## Installing using GitHub

Install PostgreSQL and create db

```bash
git clone [https://github.com/pawunder/airport-app.git](https://github.com/pawunder/airport-app.git)
cd airport-app
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python data.py
python manage.py runserver
