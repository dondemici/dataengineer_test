#created 25Jul2021 by dondemici

import pandas as pd
import mysql.connector as msql
from mysql.connector import Error

customer = pd.read_csv('db\customer.csv', index_col=False, delimiter = ',')
print(customer.head())

#Create Schema in MySQL Workbench
try:
    scdb = msql.connect(
        host="localhost",
        user="root",
        password="r!s3@b0V3"
    )
    if scdb.is_connected():
        cursor = scdb.cursor()
        cursor.execute("CREATE DATABASE starcraft_db")
        print("Database is created")
except Error as e:
    print("Error while connecting to MySQL", e)

#Insert the converted tbl files
try:
    scdb = msql.connect(
        host="localhost",
        user="root",
        password="",
        database="starcraft_db"
    )
    if scdb.is_connected():
        cursor = scdb.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        cursor.execute('DROP TABLE IF EXISTS employee_data;')
        print('Creating table....')
        # in the below line please pass the create table statement which you want #to create
        cursor.execute("CREATE TABLE customer(c_custkey varchar(45), c_name varchar(45),\
            c_address varchar(255),c_nationkey varchar(45),c_phone varchar(45),c_acctbal varchar(45),\
            c_mktsegment varchar(45),c_comment varchar(255))")
        print("Table is created....")
        #loop through the data frame
        for i,row in customer.iterrows():
            #here %S means string values 
            sql = "INSERT INTO starcraft_db.customer VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, tuple(row))
            print("Record inserted")
            # the connection is not auto committed by default, so we must commit to save our changes
            scdb.commit()
except Error as e:
            print("Error while connecting to MySQL", e)


#mycursor.execute("CREATE TABLE lineitem (l_id VARCHAR(45), l_orderkey VARCHAR(45), l_ps_id VARCHAR(45), l_linenumber VARCHAR(45), l_quantity VARCHAR(45), l_extendedprice VARCHAR(45), l_discount VARCHAR(45), l_tax VARCHAR(45), l_returnflag VARCHAR(45), l_linestatus VARCHAR(45), l_shipdate VARCHAR(45), l_commitdate VARCHAR(45), l_receiptdate VARCHAR(45), l_shipinstruct VARCHAR(45), l_shipmode VARCHAR(45), l_comment VARCHAR(255))")
#mycursor.execute("CREATE TABLE nation (n_nationkey VARCHAR(45), n_name VARCHAR(45), n_regionkey VARCHAR(45), n_comment VARCHAR(255))")
#mycursor.execute("CREATE TABLE orders (o_orderkey VARCHAR(45), o_custkey VARCHAR(45), o_orderstatus VARCHAR(45), o_totalprice VARCHAR(45), o_orderdate VARCHAR(45), o_orderpriority VARCHAR(45), o_cleark VARCHAR(45), o_shippriority VARCHAR(45), o_comment VARCHAR(255))")
#mycursor.execute("SHOW TABLES")
#for x in mycursor:
#  print(x)
