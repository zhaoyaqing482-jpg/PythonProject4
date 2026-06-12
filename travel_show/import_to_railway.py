import pymysql
import json
from decimal import Decimal

# 读取本地数据
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 连接 Railway MySQL
conn = pymysql.connect(
    host='thomas.proxy.rlwy.net',
    user='root',
    password='iQwOjhamPfyywKbqruZfcfglpiJsmwrC',
    database='railway',
    port=53687,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

for table, rows in data.items():
    if not rows:
        continue

    # 获取列名
    columns = list(rows[0].keys())
    cols_str = ', '.join([f'`{c}`' for c in columns])
    placeholders = ', '.join(['%s'] * len(columns))

    # 删除旧表（如果存在）
    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

    # 创建表
    col_defs = []
    for col in columns:
        val = rows[0][col]
        if isinstance(val, bool):
            col_defs.append(f"`{col}` TINYINT(1)")
        elif isinstance(val, int):
            col_defs.append(f"`{col}` INT")
        elif isinstance(val, float):
            col_defs.append(f"`{col}` FLOAT")
        else:
            col_defs.append(f"`{col}` TEXT")

    create_sql = f"CREATE TABLE `{table}` ({', '.join(col_defs)})"
    cursor.execute(create_sql)

    # 插入数据
    insert_sql = f"INSERT INTO `{table}` ({cols_str}) VALUES ({placeholders})"
    values = []
    for row in rows:
        row_values = []
        for col in columns:
            val = row.get(col)
            if isinstance(val, Decimal):
                val = float(val)
            row_values.append(val)
        values.append(row_values)

    cursor.executemany(insert_sql, values)
    print(f"导入 {table}: {len(rows)} 条记录")

conn.commit()
conn.close()
print("导入完成！")