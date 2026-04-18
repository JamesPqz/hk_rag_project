from sqlalchemy import text

from backend.cache.redis_client import redis_client
from backend.db.session import SessionLocal, init_db

# 创建表
init_db()
print("数据库表创建成功")

try:
    db = SessionLocal()
    db.execute(text('select 1'))
    print('success')
except Exception as e:
    print(f'fail-{e}')


try:
    redis_client.set('test', 'ok', ttl = 10)
    rlt = redis_client.get('test')
    print('success')
except Exception as e:
    print(f'fail-{e}')
