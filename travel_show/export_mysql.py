import pymysql
import json
from decimal import Decimal
from datetime import date, datetime

# 自定义 JSON 编码器
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

# 连接本地 MySQL
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='Xwc567890123#',
    database='travel_demo',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES")
tables = [row[f'Tables_in_travel_demo'] for row in cursor.fetchall()]

data = {}
for table in tables:
    cursor.execute(f"SELECT * FROM `{table}`")
    data[table] = cursor.fetchall()
    print(f"导出 {table}: {len(data[table])} 条记录")

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomEncoder)

print("导出完成！")