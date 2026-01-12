from fastapi import Depends
from typing import Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.oa_department_do import OaDepartment
from module_admin.entity.do.role_do import SysRoleDept
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from config.get_db import get_db


class GetDataScope:
    """
    获取当前用户数据权限对应的查询sql语句
    """

    DATA_SCOPE_ALL = '1'
    DATA_SCOPE_CUSTOM = '2'
    DATA_SCOPE_DEPT = '3'
    DATA_SCOPE_DEPT_AND_CHILD = '4'
    DATA_SCOPE_SELF = '5'

    def __init__(
        self,
        query_alias: Optional[str] = '',
        db_alias: Optional[str] = 'db',
        user_alias: Optional[str] = 'user_id',
        dept_alias: Optional[str] = 'dept_id',
    ):
        """
        获取当前用户数据权限对应的查询sql语句

        :param query_alias: 所要查询表对应的sqlalchemy模型名称，默认为''
        :param db_alias: orm对象别名，默认为'db'
        :param user_alias: 用户id字段别名，默认为'user_id'
        :param dept_alias: 部门id字段别名，默认为'dept_id'
        """
        self.query_alias = query_alias
        self.db_alias = db_alias
        self.user_alias = user_alias
        self.dept_alias = dept_alias

    async def __call__(
        self,
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
        query_db: AsyncSession = Depends(get_db),
    ):
        user_id = current_user.user.user_id
        dept_id = current_user.user.dept_id
        
        # 获取当前部门的 code（用于子部门查询）
        # 管理员账户可能没有部门（dept_id 为 None）
        dept_code = ''
        if dept_id is not None:
            dept = (
                await query_db.execute(select(OaDepartment).where(OaDepartment.id == dept_id))
            ).scalars().first()
            if dept:
                dept_code = dept.code or ''
        
        custom_data_scope_role_id_list = [
            item.role_id for item in current_user.user.role if item.data_scope == self.DATA_SCOPE_CUSTOM
        ]
        param_sql_list = []
        for role in current_user.user.role:
            if current_user.user.admin or role.data_scope == self.DATA_SCOPE_ALL:
                param_sql_list = ['1 == 1']
                break
            elif role.data_scope == self.DATA_SCOPE_CUSTOM:
                if len(custom_data_scope_role_id_list) > 1:
                    param_sql_list.append(
                        f"{self.query_alias}.{self.dept_alias}.in_(select(SysRoleDept.dept_id).where(SysRoleDept.role_id.in_({custom_data_scope_role_id_list}))) if hasattr({self.query_alias}, '{self.dept_alias}') else 1 == 0"
                    )
                else:
                    param_sql_list.append(
                        f"{self.query_alias}.{self.dept_alias}.in_(select(SysRoleDept.dept_id).where(SysRoleDept.role_id == {role.role_id})) if hasattr({self.query_alias}, '{self.dept_alias}') else 1 == 0"
                    )
            elif role.data_scope == self.DATA_SCOPE_DEPT:
                # 管理员账户可能没有部门
                if dept_id is not None:
                    param_sql_list.append(
                        f"{self.query_alias}.{self.dept_alias} == {dept_id} if hasattr({self.query_alias}, '{self.dept_alias}') else 1 == 0"
                    )
                else:
                    # 没有部门，返回空结果
                    param_sql_list.append('1 == 0')
            elif role.data_scope == self.DATA_SCOPE_DEPT_AND_CHILD:
                # 使用 code LIKE 替代 ancestors 查询
                if dept_id is not None and dept_code:
                    param_sql_list.append(
                        f"{self.query_alias}.{self.dept_alias}.in_(select(OaDepartment.id).where(or_(OaDepartment.id == {dept_id}, OaDepartment.code.like('{dept_code}%')))) if hasattr({self.query_alias}, '{self.dept_alias}') else 1 == 0"
                    )
                elif dept_id is not None:
                    # 如果没有 code，只查询当前部门
                    param_sql_list.append(
                        f"{self.query_alias}.{self.dept_alias} == {dept_id} if hasattr({self.query_alias}, '{self.dept_alias}') else 1 == 0"
                    )
                else:
                    # 没有部门，返回空结果
                    param_sql_list.append('1 == 0')
            elif role.data_scope == self.DATA_SCOPE_SELF:
                param_sql_list.append(
                    f"{self.query_alias}.{self.user_alias} == {user_id} if hasattr({self.query_alias}, '{self.user_alias}') else 1 == 0"
                )
            else:
                param_sql_list.append('1 == 0')
        param_sql_list = list(dict.fromkeys(param_sql_list))
        param_sql = f"or_({', '.join(param_sql_list)})" if param_sql_list else '1 == 1'

        return param_sql
