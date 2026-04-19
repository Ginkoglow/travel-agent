from db.mysql_conn import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ 数据库连接成功！")
except Exception as e:
    print("❌ 连接失败，原因：", e)