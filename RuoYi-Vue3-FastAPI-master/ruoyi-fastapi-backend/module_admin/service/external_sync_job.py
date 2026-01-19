"""
外部数据库同步定时任务
每天凌晨3:00执行一次
"""
from datetime import datetime
from module_admin.service.external_sync_service import ExternalSyncService
from utils.log_util import logger


async def sync_external_database_job():
    """
    外部数据库同步定时任务
    每天凌晨3:00执行一次，同步 oa_department、oa_employee_primary、oa_rank 三张表
    
    :return: None
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"开始执行外部数据库同步任务: {current_time}")
    
    try:
        # 同步所有表
        results = await ExternalSyncService.sync_all_tables()
        
        # 统计结果
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        logger.info(f"外部数据库同步任务完成: {current_time}, 成功: {success_count}/{total_count}")
        
        # 记录详细结果
        for table_name, success in results.items():
            if success:
                logger.info(f"  - {table_name}: 同步成功")
            else:
                logger.warning(f"  - {table_name}: 同步失败")
                
    except Exception as e:
        logger.error(f"外部数据库同步任务异常: {current_time}, 错误: {str(e)}", exc_info=True)
