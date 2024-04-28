# 7330_project
## Create the Database

1. Install MySQL
2. Open the MySQL command line and run ```CREATE DATABASE project;```
3. Update the user credentials in config.txt
4. Run main.py with ```python create_tables.py``` to create the tables

## Start the Fast API Server
Start the server with:
```uvicorn main:app --reload```

Then visit [http://localhost:8000/docs](http://localhost:8000/docs) to view the API documentation.

## Interact with the Database

Open the html file in the frontend directory.
