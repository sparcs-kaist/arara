
conn = None
def get_database_connection():
    '''Factory method to create database connection.'''
    global conn
    if not conn:
        import sqlite3
        conn = sqlite3.connect(':memory:')
    return conn
