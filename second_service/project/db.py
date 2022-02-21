import sqlite3

con = sqlite3.connect('service.db')


def db_init(c: sqlite3.Connection) -> None:
    cursor = c.cursor()
    cursor.execute(
        """CREATE TABLE catalog (product_name varchar(255) NOT NULL, 
                                price decimal(5, 2) DEFAULT 0.00);""")
    cursor.execute("""INSERT INTO catalog VALUES ('Хлеб', 25.00), 
                                                 ('Колбаса', 75.00),
                                                 ('Сыр', 54.00),
                                                 ('Молок', 86.50)""")
    con.commit()
    con.close()


if __name__ == '__main__':
    db_init(con)
