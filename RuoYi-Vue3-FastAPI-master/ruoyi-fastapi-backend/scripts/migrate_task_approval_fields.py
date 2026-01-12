#!/usr/bin/env python3
"""
数据库迁移脚本：为proj_task表添加审批相关字段
执行日期：2025-01-17
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
    
    # MySQL迁移SQL
    mysql_sqls = [
        "ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）'",
        "ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）'",
        "ALTER TABLE proj_task MODIFY COLUMN assignee VARCHAR(64) NULL COMMENT '负责人工号'",
    ]
    
    # PostgreSQL迁移SQL
    postgresql_sqls = [
        "ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL",
        "COMMENT ON COLUMN proj_task.approval_type IS '审批模式（specified-指定编制审批，sequential-逐级审批）'",
        "ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL",
        "COMMENT ON COLUMN proj_task.approval_levels IS '审批层级数组（JSON格式，存储岗位编制ID列表）'",
        "COMMENT ON COLUMN proj_task.assignee IS '负责人工号'",
    ]
    
    sqls = mysql_sqls if db_type == "mysql" else postgresql_sqls
    
    async with async_engine.begin() as conn:
        for i, sql in enumerate(sqls, 1):
            try:
                logger.info(f"执行SQL {i}/{len(sqls)}: {sql[:80]}...")
                await conn.execute(text(sql))
                logger.info(f"✓ SQL {i} 执行成功")
            except Exception as e:
                # 检查是否是字段已存在的错误
                error_msg = str(e).lower()
                if "duplicate column" in error_msg or "already exists" in error_msg or "column" in error_msg and "exists" in error_msg:
                    logger.warning(f"⚠ SQL {i} 跳过：字段可能已存在 - {str(e)}")
                else:
                    logger.error(f"✗ SQL {i} 执行失败: {str(e)}")
                    raise
    
    logger.info("数据库迁移完成！")


if __name__ == "__main__":
    try:
        asyncio.run(execute_migration())
        print("\n✅ 迁移成功完成！")
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        print(f"\n❌ 迁移失败: {str(e)}")
        sys.exit(1)
