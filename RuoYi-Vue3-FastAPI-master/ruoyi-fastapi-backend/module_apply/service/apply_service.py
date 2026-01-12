"""
申请单服务
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.dao.apply_dao import ApplyDao
from module_apply.entity.do.apply_primary_do import ApplyPrimary
from module_apply.utils.apply_id_generator import ApplyIdGenerator
from utils.log_util import logger
from exceptions.exception import ServiceException


class ApplyService:
    """申请单服务"""
    
    @staticmethod
    async def create_apply(
        query_db: AsyncSession,
        apply_type: int,
        apply_id: str = None
    ) -> ApplyPrimary:
        """
        创建申请单
        
        :param query_db: orm对象
        :param apply_type: 申请类型（1-项目推进任务）
        :param apply_id: 申请单ID（如果提供则使用，否则自动生成）
        :return: 创建的申请单对象
        """
        # 生成申请单ID
        if not apply_id:
            generator = ApplyIdGenerator.get_instance()
            apply_id = generator.generate()
        
        # 检查申请单ID是否已存在
        existing = await ApplyDao.get_apply_by_id(query_db, apply_id)
        if existing:
            raise ServiceException(message=f'申请单ID已存在: {apply_id}')
        
        # 创建申请单
        apply_data = {
            'apply_type': apply_type,
            'apply_id': apply_id,
            'apply_status': 0,  # 审批中
            'create_time': datetime.now(),
            'update_time': datetime.now(),
        }
        
        apply = await ApplyDao.create_apply(query_db, apply_data)
        logger.info(f'创建申请单成功: apply_id={apply_id}, apply_type={apply_type}')
        return apply
    
    @staticmethod
    async def get_apply_by_id(
        query_db: AsyncSession,
        apply_id: str
    ) -> Optional[ApplyPrimary]:
        """
        根据申请单ID查询申请单
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :return: 申请单对象或None
        """
        return await ApplyDao.get_apply_by_id(query_db, apply_id)
    
    @staticmethod
    async def update_apply_status(
        query_db: AsyncSession,
        apply_id: str,
        status: int
    ) -> None:
        """
        更新申请单状态
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param status: 新状态（0-审批中，1-完成，2-驳回，3-撤销）
        """
        await ApplyDao.update_apply_status(query_db, apply_id, status)
        logger.info(f'更新申请单状态: apply_id={apply_id}, status={status}')
