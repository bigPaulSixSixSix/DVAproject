#!/usr/bin/env python3
"""
清理测试数据脚本
用于测试准备：清空任务执行和审批相关表
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


async def clean_test_data():
    """清理测试数据"""
    db_type = DataBaseConfig.db_type
    
    logger.info(f"开始清理测试数据 - 数据库类型: {db_type}")
    
    # 清理SQL语句列表（按顺序执行，避免依赖问题）
    # 注意：虽然项目中没有外键约束，但按逻辑顺序清理更安全
    clean_sqls = [
        # 1. 清理审批日志表（最底层依赖表）
        "TRUNCATE TABLE apply_log",
        
        # 2. 清理审批规则表
        "TRUNCATE TABLE apply_rules",
        
        # 3. 清理申请单主表
        "TRUNCATE TABLE apply_primary",
        
        # 4. 清理任务申请详情表
        "TRUNCATE TABLE todo_task_apply",
        
        # 5. 清理任务执行表
        "TRUNCATE TABLE todo_task",
        
        # 6. 清理阶段执行表
        "TRUNCATE TABLE todo_stage",
    ]
    
    # PostgreSQL 使用不同的语法
    if db_type == "postgresql":
        clean_sqls = [sql.replace("TRUNCATE TABLE", "TRUNCATE TABLE") for sql in clean_sqls]
        # PostgreSQL 的 TRUNCATE 语法相同，但可能需要 CASCADE
        # 由于没有外键，不需要 CASCADE
    
    logger.info(f"共需要清理 {len(clean_sqls)} 个表")
    
    # 执行清理SQL语句
    try:
        async with async_engine.begin() as conn:
            for i, sql in enumerate(clean_sqls, 1):
                table_name = sql.split()[-1]  # 获取表名
                logger.info(f"[{i}/{len(clean_sqls)}] 清理表: {table_name}")
                await conn.execute(text(sql))
                logger.info(f"  ✓ {table_name} 清理完成")
        
        logger.info("=" * 50)
        logger.info("✅ 测试数据清理成功完成！")
        logger.info("=" * 50)
        
        # 验证清理结果
        logger.info("验证清理结果...")
        async with async_engine.begin() as conn:
            tables_to_check = [
                "todo_task",
                "todo_stage", 
                "todo_task_apply",
                "apply_primary",
                "apply_rules",
                "apply_log"
            ]
            
            for table in tables_to_check:
                if db_type == "postgresql":
                    count_sql = f"SELECT COUNT(*) FROM {table}"
                else:
                    count_sql = f"SELECT COUNT(*) FROM {table}"
                
                result = await conn.execute(text(count_sql))
                count = result.scalar()
                if count == 0:
                    logger.info(f"  ✓ {table}: {count} 条记录（已清空）")
                else:
                    logger.warning(f"  ⚠ {table}: {count} 条记录（未完全清空）")
            
            # 验证配置表数据（应该保留）
            config_tables = ["proj_task", "proj_stage"]
            for table in config_tables:
                if db_type == "postgresql":
                    count_sql = f"SELECT COUNT(*) FROM {table}"
                else:
                    count_sql = f"SELECT COUNT(*) FROM {table}"
                
                result = await conn.execute(text(count_sql))
                count = result.scalar()
                logger.info(f"  ✓ {table}: {count} 条记录（配置表，已保留）")
        
    except Exception as e:
        logger.error(f"清理测试数据失败: {str(e)}", exc_info=True)
        print(f"\n❌ 清理失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("清理测试数据脚本")
    print("=" * 50)
    print("")
    print("将清理以下表的数据：")
    print("  - todo_task (任务执行表)")
    print("  - todo_stage (阶段执行表)")
    print("  - todo_task_apply (任务申请详情表)")
    print("  - apply_primary (申请单主表)")
    print("  - apply_rules (审批规则表)")
    print("  - apply_log (审批日志表)")
    print("")
    print("将保留以下表的数据：")
    print("  - proj_task (项目任务配置表)")
    print("  - proj_stage (项目阶段配置表)")
    print("")
    print("开始清理...")
    print("")
    
    # 执行清理
    try:
        asyncio.run(clean_test_data())
        print("")
        print("✅ 清理完成！")
    except Exception as e:
        print(f"\n❌ 清理失败: {str(e)}")
        sys.exit(1)
