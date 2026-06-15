import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='estate', cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()
cursor.execute('SELECT id, email FROM users')
users = cursor.fetchall()
print(f'Users in database: {len(users)}')
for u in users:
    print(f'  - ID: {u["id"]}, Email: {u["email"]}')
conn.close()
