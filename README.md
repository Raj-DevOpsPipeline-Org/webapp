# CSYE6225-WEBAPP

A web application built for CSYE6225.

## Prerequisites

Please ensure the following is installed for the webapp to run locally.

- Python - 3.11+
- PostgreSQL
- pip

## Setup Instructions for macOS

### Setting up PostgreSQL Database

1. Access PostgreSQL:
   Use the psql command.

   ```bash
   sudo -u <db_username> psql
   ```

   Replace <db_username> with your PostgreSQL db_username or `postgres` if you're using the default superuser.

2. Create Database: (Optional)
   Once inside psql, create a new database

   ```bash
   CREATE DATABASE csye6225_db;
   ```

3. Create User and Assign Privileges:
   create a new user and assign it specific privileges on the database
   ```bash
   CREATE USER <db_username> WITH PASSWORD 'db_password';
   GRANT ALL PRIVILEGES ON DATABASE csye6225_db TO <username>;
   ```

### Clone the Repository

```bash
git clone https://github.com/RAJ-SUDHARSHAN/webapp.git
cd webapp/
```

### Setup Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Initialize Environmental Variables

Create .env file inside the webapp directory and set the variables

```bash
FLASK_APP=app
FLASK_DEBUG=True
DATABASE_URL=postgresql://<db_username>:<db_password>@localhost:5432/csye6225_db
CSV_PATH=./users.csv
```

### Setting up Database Migrations with Flask-Migrate

1. Initialize migrations:
   ```bash
   flask db init
   ```
2. Create migration:
   ```bash
   flask db migrate -m "Description of the changes"
   ```
3. Apply migrations:
   ```bash
   flask db upgrade
   ```

### Populate the Database (Optional)

To populate the values from the csv file, execute this command.

```bash
flask populate_db
```

### Running the Application

```bash
flask run --port 5000
```

### Test the Health of the Application

Once the application is running, check if the database and application are properly connected by accessing the `healthz` endpoint. A 200 status code indicates that the connection is successful.

To test, execute the below command in the terminal.

```bash
curl -vvvv http://localhost:5000/healthz
```
