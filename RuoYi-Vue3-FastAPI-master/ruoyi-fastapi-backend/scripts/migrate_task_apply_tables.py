#!/usr/bin/env python3
"""
数据库迁移脚本：创建任务生成、分发与审批系统相关表
执行日期：2025-01-20
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量（如果需要）
if not os.getenv("APP_ENV"):
    os.environ["APP_ENV"] = "dev"

try:
    from sqlalchemy import text
    from config.database import async_engine
    from config.env import DataBaseConfig
    from utils.log_util import logger
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)


async def execute_migration():
    """执行数据库迁移"""
    db_type = DataBaseConfig.db_type
    
    logger.info(f"开始执行数据库迁移 - 数据库类型: {db_type}")
    
    # 读取SQL文件
    if db_type == "mysql":
        sql_file = project_root / "backup/apply/数据库设计SQL_MySQL.sql"
    else:
        sql_file = project_root / "backup/apply/数据库设计SQL_PostgreSQL.sql"
    
    if not sql_file.exists():
        logger.error(f"SQL文件不存在: {sql_file}")
        sys.exit(1)
    
    # 读取SQL内容
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割SQL语句（按分号和换行）
    sql_statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current_statement += line + '\n'
        
        if line.endswith(';'):
            sql_statements.append(current_statement.strip())
            current_statement = ""
    
    if current_statement.strip():
        sql_statements.append(current_statement.strip())
    
    logger.info(f"共找到 {len(sql_statements)} 条SQL语句")
    
    # 执行SQL语句
    async with async_engine.begin() as conn:
        for i, sql in enumerate(sql_statements, 1):
            try:
                logger.info(f"执行SQL语句 {i}/{len(sql_statements)}")
                await conn.execute(text(sql))
                logger.info(f"✅ SQL语句 {i} 执行成功")
            except Exception as e:
                # 如果是"表已存在"或"列已存在"的错误，继续执行
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate column' in error_msg or 'exists' in error_msg:
                    logger.warning(f"⚠️  SQL语句 {i} 跳过（表/列已存在）: {e}")
                    continue
                else:
                    logger.error(f"❌ SQL语句 {i} 执行失败: {e}")
                    logger.error(f"SQL内容: {sql[:200]}...")
                    raise
    
    logger.info("✅ 数据库迁移完成")


if __name__ == "__main__":
    try:
        asyncio.run(execute_migration())
        print("\n✅ 数据库迁移成功完成！")
    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
