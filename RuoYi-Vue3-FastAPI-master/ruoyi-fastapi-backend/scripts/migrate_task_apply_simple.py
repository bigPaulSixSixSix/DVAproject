#!/usr/bin/env python3
"""
简化的数据库迁移脚本：创建任务生成、分发与审批系统相关表
使用pymysql直接连接数据库
"""
import sys
import re
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pymysql
except ImportError:
    print("错误: 需要安装pymysql")
    print("请运行: pip install pymysql")
    sys.exit(1)

# 从环境配置读取数据库信息
try:
    from config.env import DataBaseConfig
    
    db_config = {
        'host': DataBaseConfig.db_host,
        'port': DataBaseConfig.db_port,
        'user': DataBaseConfig.db_username,
        'password': DataBaseConfig.db_password,
        'database': DataBaseConfig.db_database,
        'charset': 'utf8mb4'
    }
    
    db_type = DataBaseConfig.db_type
except Exception as e:
    print(f"读取配置失败: {e}")
    print("使用默认配置...")
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'root1234',
        'database': 'ruoyi-fastapi',
        'charset': 'utf8mb4'
    }
    db_type = 'mysql'

if db_type != 'mysql':
    print(f"当前数据库类型为 {db_type}，此脚本仅支持MySQL")
    print("PostgreSQL请手动执行SQL文件中的PostgreSQL部分")
    sys.exit(1)

# 读取SQL文件
sql_file = project_root / "backup/apply/数据库设计SQL_MySQL.sql"
if not sql_file.exists():
    print(f"错误: SQL文件不存在: {sql_file}")
    sys.exit(1)

# 读取SQL内容
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 分割SQL语句（忽略注释和空行）
sql_statements = []
current_statement = ""

for line in sql_content.split('\n'):
    line = line.strip()
    # 跳过注释和空行
    if not line or line.startswith('--'):
        continue
    
    current_statement += line + ' '
    
    # 如果行以分号结尾，说明是一个完整的SQL语句
    if line.endswith(';'):
        sql_statements.append(current_statement.strip())
        current_statement = ""

# 如果还有未完成的语句
if current_statement.strip():
    sql_statements.append(current_statement.strip())

print(f"连接到数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
print(f"用户: {db_config['user']}")
print(f"共找到 {len(sql_statements)} 条SQL语句")
print()

try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    print("开始执行迁移...")
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, sql in enumerate(sql_statements, 1):
        try:
            # 显示SQL的前50个字符
            sql_preview = sql[:60].replace('\n', ' ').replace('\r', ' ')
            print(f"[{i}/{len(sql_statements)}] 执行: {sql_preview}...")
            
            cursor.execute(sql)
            connection.commit()
            print(f"  ✓ 成功")
            success_count += 1
        except pymysql.Error as e:
            error_code, error_msg = e.args
            # 检查是否是表已存在的错误
            if error_code == 1050:  # Table already exists
                print(f"  ⚠ 跳过：表已存在")
                skip_count += 1
            elif error_code == 1060:  # Duplicate column name
                print(f"  ⚠ 跳过：字段已存在")
                skip_count += 1
            else:
                print(f"  ✗ 失败: {error_msg} (错误码: {error_code})")
                error_count += 1
                # 继续执行，不中断
        except Exception as e:
            print(f"  ✗ 失败: {str(e)}")
            error_count += 1
    
    cursor.close()
    connection.close()
    
    print()
    print("=" * 60)
    print(f"迁移完成！")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ⚠ 跳过: {skip_count}")
    print(f"  ✗ 失败: {error_count}")
    print("=" * 60)
    
    if error_count > 0:
        print("\n⚠️  有部分SQL执行失败，请检查上面的错误信息")
        sys.exit(1)
    else:
        print("\n✅ 数据库迁移成功完成！")
    
except pymysql.Error as e:
    print(f"\n❌ 数据库连接错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
