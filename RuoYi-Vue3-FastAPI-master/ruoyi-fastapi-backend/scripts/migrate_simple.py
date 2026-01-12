#!/usr/bin/env python3
"""
简化的数据库迁移脚本：为proj_task表添加审批相关字段
使用pymysql直接连接数据库
"""
import sys
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

# MySQL迁移SQL
sqls = [
    "ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）'",
    "ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）'",
    "ALTER TABLE proj_task MODIFY COLUMN assignee VARCHAR(64) NULL COMMENT '负责人工号'",
]

print(f"连接到数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
print(f"用户: {db_config['user']}")
print()

try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    print("开始执行迁移...")
    for i, sql in enumerate(sqls, 1):
        try:
            print(f"[{i}/{len(sqls)}] 执行: {sql[:60]}...")
            cursor.execute(sql)
            connection.commit()
            print(f"  ✓ 成功")
        except pymysql.Error as e:
            error_code, error_msg = e.args
            # 检查是否是字段已存在的错误
            if error_code == 1060:  # Duplicate column name
                print(f"  ⚠ 跳过：字段已存在")
            else:
                print(f"  ✗ 失败: {error_msg}")
                raise
    
    cursor.close()
    connection.close()
    
    print()
    print("✅ 迁移成功完成！")
    
except pymysql.Error as e:
    print(f"❌ 数据库错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
