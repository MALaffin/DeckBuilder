# following tutorial from https://www.freecodecamp.org/news/connect-python-with-sql/

import mysql.connector
from mysql.connector import Error
import pandas as pd


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def create_database(connection, name):
    cursor = connection.cursor()
    try:
        cmd = 'CREATE DATABASE IF NOT EXISTS ' + name
        cursor.execute(cmd)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


def remove_database(connection, name):
    cursor = connection.cursor()
    try:
        cmd = 'DROP DATABASE IF EXISTS ' + name
        cursor.execute(cmd)
        print("Database removed successfully")
    except Error as err:
        print(f"Error: '{err}'")


# def create_db_connection(host_name, user_name, user_password, db_name):
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host=host_name,
#             user=user_name,
#             passwd=user_password,
#             database=db_name
#         )
#         print("MySQL Database connection successful")
#     except Error as err:
#         print(f"Error: '{err}'")
#     return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


def doNotThrashTheDisk(connection, buffer):
    cursor = connection.cursor()
    try:
        cmd = 'SET GLOBAL Innodb_buffer_pool_size = ' + str(buffer)
        cursor.execute(cmd)
        cmd = 'SET GLOBAL innodb_flush_log_at_trx_commit = 2'
        cursor.execute(cmd)
        connection.commit()
        print("buffer " + str(buffer) + " successful")
    except Error as err:
        print(f"Error: '{err}'")


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


def dbExist(connection, dbName):
    cmd = 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = "' + dbName + '"'
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(cmd)
        result = cursor.fetchall()
        return len(result) == 1
    except Error as err:
        print(f"Error: '{err}'")
    return None


def parseDbTable(connection, db, table, columns):
    cmd1 = 'USE ' + db
    cmd2 = 'SELECT * FROM ' + table
    cursor = connection.cursor()
    results = None  # tuples
    try:
        cursor.execute(cmd1)
        cursor.execute(cmd2)
        results = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        return None
    return results
    # from_db = []
    # for result in results:
    #     result = list(result)
    #     from_db.append(result)
    # df = pd.DataFrame(from_db, columns=columns)
    # return df
def parseDbTable(connection, db, table):
    cmd1 = 'USE ' + db
    cmd2 = 'SELECT * FROM ' + table
    cursor = connection.cursor()
    results = None  # tuples
    try:
        cursor.execute(cmd1)
        cursor.execute(cmd2)
        results = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        return None
    return results
    # from_db = []
    # for result in results:
    #     result = list(result)
    #     from_db.append(result)
    # df = pd.DataFrame(from_db, columns=columns)
    # return df


def createTable(connection, db, table, columns):
    cmd1 = 'USE ' + db
    cmd2 = 'CREATE TABLE ' + table + ' ' + columns
    cursor = connection.cursor()
    results = None  # tuples
    try:
        cursor.execute(cmd1)
        cursor.execute(cmd2)
    except Error as err:
        print(f"Error: '{err}'")


def showTables(connection, db):
    cmd = 'USE ' + db
    cursor = connection.cursor()
    results = None  # tuples
    try:
        cursor.execute(cmd)
        cursor.execute('show tables')
        results = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        return None
    from_db = []
    for result in results:
        result = list(result)
        from_db.append(result)
    df = pd.DataFrame(from_db, columns=None)
    print(df)
    return df


def autoCommit(connection, state):
    cmd = 'SET autocommit='+state
    cursor = connection.cursor()
    try:
        cursor.execute(cmd)
    except Error as err:
        print(f"Error: '{err}'")


def showTable(connection, db, table):
    cmd1 = 'USE ' + db
    cmd2 = 'DESCRIBE ' + table
    cmd3 = 'Select count(*) from ' + table
    cursor = connection.cursor()
    results = None  # tuples
    try:
        cursor.execute(cmd3)
        results = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        return None
    from_db = []
    for result in results:
        result = list(result)
        from_db.append(result)
    df = pd.DataFrame(from_db, columns=None)
    print(df)
    try:
        cursor.execute(cmd1)
        cursor.execute(cmd2)
        results = cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")
        return None
    from_db = []
    for result in results:
        result = list(result)
        from_db.append(result)
    df = pd.DataFrame(from_db, columns=None)
    print(df)
    return df


def viewResults(results, columns):
    from_db = []
    for result in results:
        result = list(result)
        from_db.append(result)
    df = pd.DataFrame(from_db, columns=columns)
    print(df)


def showDatabases(connection):
    res = read_query(connection, 'show databases;')
    viewResults(res, ['Database'])


def moveDatabaseInfoWithSubSelect(connection, source, rows, oldCols, destination, newCols, primary, maxSelect):
    #https://stackoverflow.com/questions/6860746/sql-selecting-multiple-columns-based-on-max-value-in-one-column
    #todo remove the hardcoded availability like paper constraint; maybe move this method to MtgDbHelper
    oldCols = oldCols.replace(primary, 't.'+primary)
    rows = rows.replace(primary, 't.'+primary)
    oldCols = oldCols.replace('side', 't.side')
    rows = rows.replace('side', 't.side')
    cmd =   'INSERT INTO ' + destination + ' (' + newCols + ')' + """ 
                SELECT """ + oldCols + """ 
                FROM """ + source + """ as t
                    INNER JOIN(
                        SELECT """ + primary + ', side, MAX(' + maxSelect + ') as maxTmp' + """
                        FROM """ + source + """ where availability like '%paper%'
                        GROUP BY """ + primary + """, side) AS tmp 
                    ON t.""" + primary + ' = tmp.' + primary + """
                        AND t.""" + maxSelect + """ = tmp.maxTmp
                        AND (t.side = tmp.side OR t.side IS NULL)
                WHERE """ + rows
            # pretty sure this is where Everythingamajig variants are lost

    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(cmd)
    except Error as err:
        print(f"Error: '{err}'")


def moveDatabaseInfo(connection, source, rows, oldCols, destination, newCols):
    #todo consider making distict an option
    cmd = 'INSERT INTO ' + destination + ' (' + newCols + ')' + """ 
        SELECT DISTINCT """ + oldCols + """
        FROM """ + source + """
        WHERE """ + rows
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(cmd)
    except Error as err:
        print(f"Error: '{err}'")

def AddCol(connection, db, table, colName, condition):
    #todo consider making distict an option
    cmd0 = "use " + db +";"
    cmd1 = "alter table `"+table+"` add `"+colName+"` bool default False;" 
    cmd2 = "UPDATE "+table +" SET "+colName+" = "+condition+";"
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(cmd0)
        cursor.execute(cmd1)
        cursor.execute(cmd2)
    except Error as err:
        print(f"Error: '{err}'")


# TODO consider making some methods for these:
# show databases;
# drop database test;
# consider passing the cursor instead of connection
# show databases;
# use databasename;
# show tables;
# Select count(*) from cards;
# SELECT DATA_TYPE from INFORMATION_SCHEMA. COLUMNS where table_schema = 'MTG_FULL' and table_name = 'cards';
