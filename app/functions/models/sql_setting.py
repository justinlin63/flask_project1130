import mysql.connector

conn = mysql.connector.connect(
    host='192.168.1.110',  # 主機名稱
    database='flask_project1130',  # 資料庫名稱
    user='root',  # 帳號
    password='admin')  # 密碼
cursor = conn.cursor()
# 連接資料庫
# 建立使用者資料表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id int PRIMARY KEY AUTO_INCREMENT,
        username varchar(50) NOT NULL,
        password varchar(500) NOT NULL,
        role varchar(50) NOT NULL,
        email varchar(50) NOT NULL,
        reset_password_token varchar(500) NOT NULL,
        money int NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id int PRIMARY KEY AUTO_INCREMENT NOT NULL,
        user_id varchar(45) NOT NULL,
        cart int NOT NULL,
        quantity int NOT NULL 
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS media (
        id int PRIMARY KEY  NOT NULL,
        file_name varchar(1000) NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id int PRIMARY KEY AUTO_INCREMENT NOT NULL,
        username varchar(45) NOT NULL,
        product_id varchar(1000) NOT NULL,
        quantity varchar(1000) NOT NULL,
        status varchar(45) NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id int PRIMARY KEY AUTO_INCREMENT NOT NULL,
        name varchar(45) NOT NULL,
        price INT NOT NULL,
        hot INT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pay_list (
        id int PRIMARY KEY AUTO_INCREMENT NOT NULL,
        token varchar(100) NOT NULL UNIQUE,
        user_id int NOT NULL,
        to_user_id int NOT NULL,
        money INT NOT NULL,
        cart varchar(1000) not null,
        quantity varchar(1000) not null,
        time INT NOT NULL,
        status varchar(50) NOT NULL
    )
''')
conn.commit()
conn.close()
