"""
系统初始化工具：初始化管理员账户
"""
from sqlalchemy import select
from datetime import datetime
from config.database import AsyncSessionLocal
from module_admin.entity.do.sys_user_local_do import SysUserLocal
from utils.pwd_util import PwdUtil
from utils.log_util import logger


async def init_admin_user():
    """
    初始化管理员账户
    如果管理员账户不存在，则创建一个默认的管理员账户
    
    :return: None
    """
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已存在管理员账户（employee_id = 0 表示管理员）
            existing_admin = await db.execute(
                select(SysUserLocal).where(SysUserLocal.employee_id == 0)
            )
            admin_user = existing_admin.scalar_one_or_none()
            
            if admin_user:
                # 管理员账户已存在，检查是否需要更新
                logger.info(f"管理员账户已存在: {admin_user.job_number}")
                # 确保管理员账户是启用状态
                if admin_user.enable != '1':
                    admin_user.enable = '1'
                    admin_user.status = '0'
                    await db.commit()
                    logger.info("管理员账户已更新为启用状态")
                return
            
            # 创建默认管理员账户
            default_password = 'admin123456'  # 默认密码
            hashed_password = PwdUtil.get_password_hash(default_password)
            
            admin_user = SysUserLocal(
                employee_id=0,  # 0 表示管理员账户，不关联真实员工表
                job_number='admin',  # 默认管理员账号
                password=hashed_password,
                status='0',  # 正常状态
                enable='1',  # 启用
                create_by='system',
                create_time=datetime.now(),
                update_by='system',
                update_time=datetime.now(),
                remark='系统管理员账户（自动创建）'
            )
            
            db.add(admin_user)
            await db.commit()
            logger.info(f"管理员账户创建成功: admin (默认密码: {default_password})")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"初始化管理员账户失败: {str(e)}", exc_info=True)
            raise
