from database import engine

try:
    connection = engine.connect()
    print("PostgreSQL Connected Successfully!")
    connection.close()
except Exception as e:
    print("Database Connection Failed!")
    print(e)