from sqlalchemy import bindparam, func, or_, select, update  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import immutabledict
from typing import List
from module_admin.entity.do.oa_department_do import OaDepartment
from module_admin.entity.do.role_do import SysRoleDept  # noqa: F401
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.vo.dept_vo import DeptModel

# 确保在 eval() 执行时这些类可以被访问
# 这些导入是为了在 data_scope.py 生成的 SQL 字符串中使用


class DeptDao:
    """
    部门管理模块数据库操作层
    """

    @classmethod
    async def get_dept_by_id(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id获取在用部门信息

        :param db: orm对象
        :param dept_id: 部门id
        :return: 在用部门信息对象
        """
        dept_info = (await db.execute(select(OaDepartment).where(OaDepartment.id == dept_id))).scalars().first()

        return dept_info

    @classmethod
    async def get_dept_detail_by_id(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id获取部门详细信息

        :param db: orm对象
        :param dept_id: 部门id
        :return: 部门信息对象
        """
        dept_info = (
            (await db.execute(select(OaDepartment).where(OaDepartment.id == dept_id, OaDepartment.enable == '1')))
            .scalars()
            .first()
        )

        return dept_info

    @classmethod
    async def get_dept_detail_by_info(cls, db: AsyncSession, dept: DeptModel):
        """
        根据部门参数获取部门信息

        :param db: orm对象
        :param dept: 部门参数对象
        :return: 部门信息对象
        """
        dept_info = (
            (
                await db.execute(
                    select(OaDepartment).where(
                        OaDepartment.parent_id == dept.parent_id if dept.parent_id else True,
                        OaDepartment.name == dept.dept_name if dept.dept_name else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return dept_info

    @classmethod
    async def get_children_dept_dao(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id查询当前部门的子部门列表信息
        使用 code LIKE 替代 ancestors 查询

        :param db: orm对象
        :param dept_id: 部门id
        :return: 子部门信息列表
        """
        # 获取当前部门的code
        current_dept = await cls.get_dept_by_id(db, dept_id)
        if not current_dept or not current_dept.code:
            return []
        
        current_code = current_dept.code
        
        # 使用 code LIKE 查询子部门
        dept_result = (
            (await db.execute(
                select(OaDepartment)
                .where(
                    OaDepartment.code.like(f'{current_code}%'),
                    OaDepartment.id != dept_id,  # 排除自己
                )
            )).scalars().all()
        )

        return dept_result

    @classmethod
    async def get_dept_list_for_tree(cls, db: AsyncSession, dept_info: DeptModel, data_scope_sql: str):
        """
        获取所有在用部门列表信息

        :param db: orm对象
        :param dept_info: 部门对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 在用部门列表信息
        """
        # 构建查询条件
        conditions = [
            OaDepartment.status == '0',
            OaDepartment.enable == '1',
        ]
        
        # 添加名称过滤
        if dept_info.dept_name:
            conditions.append(OaDepartment.name.like(f'%{dept_info.dept_name}%'))
        
        # 添加数据权限过滤
        if data_scope_sql:
            try:
                # 确保在 eval 执行环境中可以访问到 OaDepartment
                data_scope_condition = eval(data_scope_sql)
                conditions.append(data_scope_condition)
            except Exception as e:
                # 如果 eval 失败，记录错误并返回空结果（安全策略：权限过滤失败时不显示任何数据）
                from utils.log_util import logger
                logger.error(f'部门树数据权限过滤失败: {str(e)}, data_scope_sql={data_scope_sql}')
                # 返回空结果，而不是所有部门（安全策略）
                return []
        
        dept_result = (
            (
                await db.execute(
                    select(OaDepartment)
                    .where(*conditions)
                    .order_by(OaDepartment.sort_no)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return dept_result

    @classmethod
    async def get_dept_list(cls, db: AsyncSession, page_object: DeptModel, data_scope_sql: str):
        """
        根据查询参数获取部门列表信息

        :param db: orm对象
        :param page_object: 不分页查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 部门列表信息对象
        """
        dept_result = (
            (
                await db.execute(
                    select(OaDepartment)
                    .where(
                        OaDepartment.enable == '1',
                        OaDepartment.id == page_object.dept_id if page_object.dept_id is not None else True,
                        OaDepartment.status == page_object.status if page_object.status else True,
                        OaDepartment.name.like(f'%{page_object.dept_name}%') if page_object.dept_name else True,
                    )
                    .order_by(OaDepartment.sort_no)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return dept_result

    @classmethod
    async def count_normal_children_dept_dao(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id查询查询所有子部门（正常状态）的数量
        使用 code LIKE 替代 ancestors 查询

        :param db: orm对象
        :param dept_id: 部门id
        :return: 所有子部门（正常状态）的数量
        """
        # 获取当前部门的code
        current_dept = await cls.get_dept_by_id(db, dept_id)
        if not current_dept or not current_dept.code:
            return 0
        
        current_code = current_dept.code
        
        normal_children_dept_count = (
            await db.execute(
                select(func.count('*'))
                .select_from(OaDepartment)
                .where(
                    OaDepartment.status == '0',
                    OaDepartment.enable == '1',
                    OaDepartment.code.like(f'{current_code}%'),
                    OaDepartment.id != dept_id,  # 排除自己
                )
            )
        ).scalar()

        return normal_children_dept_count

    @classmethod
    async def count_children_dept_dao(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id查询查询所有子部门（所有状态）的数量

        :param db: orm对象
        :param dept_id: 部门id
        :return: 所有子部门（所有状态）的数量
        """
        children_dept_count = (
            await db.execute(
                select(func.count('*'))
                .select_from(OaDepartment)
                .where(OaDepartment.enable == '1', OaDepartment.parent_id == dept_id)
                .limit(1)
            )
        ).scalar()

        return children_dept_count

    @classmethod
    async def count_dept_user_dao(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id查询查询部门下的用户数量

        :param db: orm对象
        :param dept_id: 部门id
        :return: 部门下的用户数量
        """
        dept_user_count = (
            await db.execute(
                select(func.count('*'))
                .select_from(OaEmployeePrimary)
                .where(
                    OaEmployeePrimary.organization_id == dept_id,
                    OaEmployeePrimary.enable == '1',
                )
            )
        ).scalar()

        return dept_user_count
