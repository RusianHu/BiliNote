import sqlite3

conn = sqlite3.connect('note_tasks.db')
cursor = conn.cursor()

# 检查表
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", tables)

# 检查video_tasks表中的数据
try:
    cursor.execute('SELECT * FROM video_tasks')
    rows = cursor.fetchall()
    print("Data in video_tasks:", rows)
except Exception as e:
    print("Error querying video_tasks:", e)

conn.close()
