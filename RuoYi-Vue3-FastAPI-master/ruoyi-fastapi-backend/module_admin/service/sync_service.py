from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from module_admin.dao.sync_dao import SyncDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.log_util import logger


class SyncService:
    """
    数据同步模块服务层
    """

    @classmethod
    async def sync_employees_services(
        cls,
        query_db: AsyncSession,
        company_id: int = 2,
        default_password: str = None,
        sync_deleted: bool = True,
    ) -> CrudResponseModel:
        """
        同步员工数据到本地用户表
        
        :param query_db: orm对象
        :param company_id: 公司ID，默认2
        :param default_password: 默认密码（新增用户时使用）
        :param sync_deleted: 是否同步删除（软删除真实表中不存在的用户）
        :return: 同步结果
        """
        try:
            # 统计信息
            stats = {
                'added': 0,      # 新增数量
                'updated': 0,    # 更新数量
                'deleted': 0,    # 删除数量
                'skipped': 0,    # 跳过数量
            }
            
            # 1. 获取需要同步的员工列表（从真实表）
            employees = await SyncDao.get_employees_to_sync(query_db, company_id)
            
            if not employees:
                return CrudResponseModel(
                    is_success=True,
                    message=f'没有需要同步的员工数据（company_id={company_id}）',
                )
            
            # 2. 获取本地已存在的用户（通过employee_id）
            employee_ids = [emp.id for emp in employees]
            local_users_dict = await SyncDao.get_local_users_by_employee_ids(query_db, employee_ids)
            
            # 3. 处理每个员工
            for employee in employees:
                try:
                    local_user = local_users_dict.get(employee.id)
                    
                    if local_user is None:
                        # 新增用户
                        await SyncDao.add_local_user_dao(query_db, employee, default_password)
                        stats['added'] += 1
                    else:
                        # 更新用户信息
                        await SyncDao.update_local_user_dao(query_db, local_user, employee)
                        stats['updated'] += 1
                
                except Exception as e:
                    logger.error(f'处理员工失败: employee_id={employee.id}, job_number={employee.job_number}, error={str(e)}')
                    stats['skipped'] += 1
                    continue
            
            # 4. 处理软删除（如果启用）
            if sync_deleted:
                await cls._sync_deleted_users(query_db, employee_ids, company_id, stats)
            
            # 5. 提交事务
            await query_db.commit()
            
            message = f'同步完成: 新增 {stats["added"]} 个，更新 {stats["updated"]} 个，删除 {stats["deleted"]} 个，跳过 {stats["skipped"]} 个'
            
            return CrudResponseModel(
                is_success=True,
                message=message,
            )
        
        except Exception as e:
            await query_db.rollback()
            logger.error(f'同步员工数据失败: {str(e)}')
            raise e

    @classmethod
    async def _sync_deleted_users(
        cls,
        query_db: AsyncSession,
        active_employee_ids: List[int],
        company_id: int,
        stats: Dict[str, int],
    ):
        """
        同步删除：软删除真实表中不存在的用户
        
        :param query_db: orm对象
        :param active_employee_ids: 真实表中存在的员工ID列表
        :param company_id: 公司ID
        :param stats: 统计信息字典
        :return: None
        """
        # 获取所有本地启用的用户
        local_users = await SyncDao.get_all_local_users(query_db)
        
        for local_user in local_users:
            # 如果本地用户的employee_id不在真实表的员工列表中，则软删除
            if local_user.employee_id not in active_employee_ids:
                # 再次确认员工是否真的不存在（防止并发问题）
                exists = await SyncDao.check_employee_exists(query_db, local_user.employee_id, company_id)
                if not exists:
                    await SyncDao.soft_delete_local_user_dao(query_db, local_user.user_id)
                    stats['deleted'] += 1

    @classmethod
    async def sync_single_employee_services(
        cls,
        query_db: AsyncSession,
        employee_id: int,
        company_id: int = 2,
        default_password: str = None,
    ) -> CrudResponseModel:
        """
        同步单个员工数据
        
        :param query_db: orm对象
        :param employee_id: 员工ID
        :param company_id: 公司ID，默认2
        :param default_password: 默认密码（新增用户时使用）
        :return: 同步结果
        """
        try:
            # 查询员工
            from sqlalchemy import select
            from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
            
            employee = (
                await query_db.execute(
                    select(OaEmployeePrimary)
                    .where(
                        OaEmployeePrimary.id == employee_id,
                        OaEmployeePrimary.company_id == company_id,
                    )
                )
            ).scalars().first()
            
            if not employee:
                return CrudResponseModel(
                    is_success=False,
                    message=f'员工不存在: employee_id={employee_id}, company_id={company_id}',
                )
            
            # 查询本地用户
            local_users_dict = await SyncDao.get_local_users_by_employee_ids(query_db, [employee_id])
            local_user = local_users_dict.get(employee_id)
            
            if local_user is None:
                # 新增用户（只有启用的员工才新增）
                if employee.enable == '1':
                    await SyncDao.add_local_user_dao(query_db, employee, default_password)
                    await query_db.commit()
                    return CrudResponseModel(
                        is_success=True,
                        message=f'新增用户成功: {employee.job_number}',
                    )
                else:
                    return CrudResponseModel(
                        is_success=False,
                        message=f'员工已禁用，不进行同步: {employee.job_number}',
                    )
            else:
                # 更新用户
                await SyncDao.update_local_user_dao(query_db, local_user, employee)
                await query_db.commit()
                return CrudResponseModel(
                    is_success=True,
                    message=f'更新用户成功: {employee.job_number}',
                )
        
        except Exception as e:
            await query_db.rollback()
            logger.error(f'同步单个员工数据失败: employee_id={employee_id}, error={str(e)}')
            raise e
