from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.oa_department_do import OaDepartment
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.sys_user_local_do import SysUserLocal


async def login_by_account(db: AsyncSession, user_name: str):
    """
    根据用户名（工号）查询用户信息
    使用本地用户表 + 真实员工表 + 部门表
    支持管理员账户（employee_id=0）

    :param db: orm对象
    :param user_name: 用户名（工号）
    :return: (SysUserLocal, OaEmployeePrimary, OaDepartment) 元组
    """
    user = (
        await db.execute(
            select(SysUserLocal, OaEmployeePrimary, OaDepartment)
            .where(
                SysUserLocal.job_number == user_name,
                SysUserLocal.enable == '1',  # 启用状态
                SysUserLocal.status == '0',  # 正常状态
            )
            .join(
                OaEmployeePrimary,
                and_(
                    SysUserLocal.employee_id == OaEmployeePrimary.id,
                    SysUserLocal.employee_id != 0,  # 管理员账户 employee_id=0，不JOIN员工表
                ),
                isouter=True,
            )
            .join(
                OaDepartment,
                and_(
                    OaEmployeePrimary.organization_id == OaDepartment.id,
                    OaDepartment.enable == '1',  # 部门启用
                ),
                isouter=True,
            )
            .distinct()
        )
    ).first()

    return user
