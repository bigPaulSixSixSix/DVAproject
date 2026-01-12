from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.sys_user_local_do import SysUserLocal
from utils.pwd_util import PwdUtil


class SyncDao:
    """
    数据同步模块数据库操作层
    """

    @classmethod
    async def get_employees_to_sync(cls, db: AsyncSession, company_id: int = 2):
        """
        获取需要同步的员工列表（从真实表）
        
        :param db: orm对象
        :param company_id: 公司ID，默认2
        :return: 员工列表
        """
        employees = (
            await db.execute(
                select(OaEmployeePrimary)
                .where(
                    OaEmployeePrimary.company_id == company_id,
                    OaEmployeePrimary.enable == '1',  # 只同步启用的员工
                )
                .order_by(OaEmployeePrimary.id)
            )
        ).scalars().all()
        
        return employees

    @classmethod
    async def get_local_users_by_employee_ids(cls, db: AsyncSession, employee_ids: list):
        """
        根据员工ID列表获取本地用户列表
        
        :param db: orm对象
        :param employee_ids: 员工ID列表
        :return: 本地用户列表（字典，key为employee_id）
        """
        if not employee_ids:
            return {}
        
        local_users = (
            await db.execute(
                select(SysUserLocal)
                .where(SysUserLocal.employee_id.in_(employee_ids))
            )
        ).scalars().all()
        
        # 转换为字典，key为employee_id
        return {user.employee_id: user for user in local_users}

    @classmethod
    async def get_all_local_users(cls, db: AsyncSession):
        """
        获取所有本地用户（用于检查需要软删除的用户）
        
        :param db: orm对象
        :return: 本地用户列表
        """
        local_users = (
            await db.execute(
                select(SysUserLocal)
                .where(SysUserLocal.enable == '1')  # 只查询启用的用户
            )
        ).scalars().all()
        
        return local_users

    @classmethod
    async def add_local_user_dao(cls, db: AsyncSession, employee: OaEmployeePrimary, default_password: str = None):
        """
        新增本地用户
        
        :param db: orm对象
        :param employee: 员工对象
        :param default_password: 默认密码（如果为None，则使用默认密码）
        :return: 新增的本地用户对象
        """
        # 如果没有提供密码，使用默认密码
        if default_password is None:
            default_password = '123456'  # 默认密码
        
        # 加密密码
        hashed_password = PwdUtil.get_password_hash(default_password)
        
        # 创建本地用户对象
        local_user = SysUserLocal(
            employee_id=employee.id,
            job_number=employee.job_number,
            password=hashed_password,
            status='0',  # 正常状态
            enable='1',  # 启用
            sync_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        
        db.add(local_user)
        await db.flush()
        
        return local_user

    @classmethod
    async def update_local_user_dao(cls, db: AsyncSession, local_user: SysUserLocal, employee: OaEmployeePrimary):
        """
        更新本地用户信息
        
        :param db: orm对象
        :param local_user: 本地用户对象
        :param employee: 员工对象
        :return: None
        """
        # 更新字段（不更新密码）
        update_data = {
            'job_number': employee.job_number,
            'sync_time': datetime.now(),
            'update_time': datetime.now(),
        }
        
        # 如果员工被禁用，则同步禁用本地用户
        if employee.enable != '1':
            update_data['enable'] = '0'
            update_data['status'] = '1'  # 停用
        
        await db.execute(
            update(SysUserLocal)
            .where(SysUserLocal.user_id == local_user.user_id)
            .values(**update_data)
        )

    @classmethod
    async def soft_delete_local_user_dao(cls, db: AsyncSession, user_id: int):
        """
        软删除本地用户（设置enable=0）
        
        :param db: orm对象
        :param user_id: 用户ID
        :return: None
        """
        await db.execute(
            update(SysUserLocal)
            .where(SysUserLocal.user_id == user_id)
            .values(
                enable='0',
                status='1',  # 停用
                update_time=datetime.now(),
            )
        )

    @classmethod
    async def check_employee_exists(cls, db: AsyncSession, employee_id: int, company_id: int = 2):
        """
        检查员工是否存在于真实表中（且启用）
        
        :param db: orm对象
        :param employee_id: 员工ID
        :param company_id: 公司ID，默认2
        :return: True/False
        """
        employee = (
            await db.execute(
                select(OaEmployeePrimary)
                .where(
                    OaEmployeePrimary.id == employee_id,
                    OaEmployeePrimary.company_id == company_id,
                    OaEmployeePrimary.enable == '1',
                )
            )
        ).scalars().first()
        
        return employee is not None
