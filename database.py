import mysql.connector

def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", #default kosong
        database="sim_db"
    )
    return conn