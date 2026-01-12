import math
import re
from datetime import datetime, time
from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.oa_department_do import OaDepartment  # noqa: F401
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.oa_rank_do import OaRank
from module_admin.entity.do.role_do import SysRole, SysRoleDept, SysRoleMenu  # noqa: F401
from module_admin.entity.do.sys_user_local_do import SysUserLocal
from module_admin.entity.do.user_do import SysUserRole
from utils.field_mapper import FieldMapper
from utils.pwd_util import PwdUtil
from module_admin.entity.vo.user_vo import (
    UserModel,
    UserPageQueryModel,
    UserRoleModel,
    UserRolePageQueryModel,
    UserRoleQueryModel,
)
from utils.page_util import PageUtil, PageResponseModel


class UserDao:
    """
    用户管理模块数据库操作层
    """

    @classmethod
    async def get_user_by_name(cls, db: AsyncSession, user_name: str):
        """
        根据用户名（工号）获取用户信息
        使用本地用户表 + 真实员工表

        :param db: orm对象
        :param user_name: 用户名（工号）
        :return: 当前用户名的用户信息对象（MappedUser）
        """
        # 查询本地用户表
        query_user_local = (
            (
                await db.execute(
                    select(SysUserLocal)
                    .where(
                        SysUserLocal.job_number == user_name,
                        SysUserLocal.enable == '1',
                        SysUserLocal.status == '0',
                    )
                    .order_by(desc(SysUserLocal.create_time))
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        if not query_user_local:
            return None
        
        # 查询员工信息（管理员账户 employee_id=0，不查询员工表）
        query_employee = None
        if query_user_local.employee_id != 0:
            query_employee = (
                (
                    await db.execute(
                        select(OaEmployeePrimary)
                        .where(OaEmployeePrimary.id == query_user_local.employee_id)
                        .distinct()
                    )
                )
                .scalars()
                .first()
            )
        
        # 使用字段映射工具转换为系统框架格式
        if query_user_local.employee_id == 0:
            # 管理员账户：使用本地用户表信息
            user_basic_info_dict = {
                'user_id': query_user_local.user_id,
                'dept_id': None,
                'user_name': query_user_local.job_number,
                'nick_name': '系统管理员',
                'user_type': '00',
                'email': '',
                'phonenumber': '',
                'sex': '0',
                'avatar': '',
                'password': query_user_local.password,
                'status': query_user_local.status,
                'del_flag': '0' if query_user_local.enable == '1' else '2',
                'login_ip': query_user_local.login_ip or '',
                'login_date': query_user_local.login_date,
                'pwd_update_date': query_user_local.pwd_update_date,
                'create_by': query_user_local.create_by or '',
                'create_time': query_user_local.create_time,
                'update_by': query_user_local.update_by or '',
                'update_time': query_user_local.update_time,
                'remark': query_user_local.remark or '',
            }
        else:
            # 普通员工：使用字段映射工具
            user_basic_info_dict = FieldMapper.map_employee_to_user_format(query_employee, query_user_local)
        
        # 创建 MappedUser 对象，用于兼容系统框架的数据格式
        class MappedUser:
            """用户数据映射类，支持属性访问"""
            def __init__(self, data: dict):
                if data:
                    for k, v in data.items():
                        setattr(self, k, v)
        
        return MappedUser(user_basic_info_dict) if user_basic_info_dict else None

    @classmethod
    async def get_user_by_info(cls, db: AsyncSession, user: UserModel):
        """
        根据用户参数获取用户信息
        使用本地用户表 + 真实员工表

        :param db: orm对象
        :param user: 用户参数
        :return: 当前用户参数的用户信息对象（MappedUser）
        """
        # 构建查询条件
        conditions = [
            SysUserLocal.enable == '1',
            SysUserLocal.status == '0',
        ]
        
        # 根据参数添加查询条件
        if user.user_name:
            conditions.append(SysUserLocal.job_number == user.user_name)
        
        # 查询员工信息以匹配手机号
        # 注意：真实表 oa_employee_primary 没有 email 字段，所以不支持根据 email 查询
        if user.phonenumber:
            # 先查询符合条件的员工ID
            employee_ids = (
                await db.execute(
                    select(OaEmployeePrimary.id)
                    .where(OaEmployeePrimary.phone == user.phonenumber)
                )
            ).scalars().all()
            
            if employee_ids:
                conditions.append(SysUserLocal.employee_id.in_(employee_ids))
            else:
                # 如果没有找到匹配的员工，返回 None
                return None
        
        # 如果查询 email，由于真实表没有 email 字段，直接返回 None
        if user.email:
            return None
        
        # 查询本地用户表
        query_user_local = (
            (
                await db.execute(
                    select(SysUserLocal)
                    .where(*conditions)
                    .order_by(desc(SysUserLocal.create_time))
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        if not query_user_local:
            return None
        
        # 查询员工信息（管理员账户 employee_id=0，不查询员工表）
        query_employee = None
        if query_user_local.employee_id != 0:
            query_employee = (
                (
                    await db.execute(
                        select(OaEmployeePrimary)
                        .where(OaEmployeePrimary.id == query_user_local.employee_id)
                        .distinct()
                    )
                )
                .scalars()
                .first()
            )
        
        # 使用字段映射工具转换为系统框架格式
        if query_user_local.employee_id == 0:
            # 管理员账户：使用本地用户表信息
            user_basic_info_dict = {
                'user_id': query_user_local.user_id,
                'dept_id': None,
                'user_name': query_user_local.job_number,
                'nick_name': '系统管理员',
                'user_type': '00',
                'email': '',
                'phonenumber': '',
                'sex': '0',
                'avatar': '',
                'password': query_user_local.password,
                'status': query_user_local.status,
                'del_flag': '0' if query_user_local.enable == '1' else '2',
                'login_ip': query_user_local.login_ip or '',
                'login_date': query_user_local.login_date,
                'pwd_update_date': query_user_local.pwd_update_date,
                'create_by': query_user_local.create_by or '',
                'create_time': query_user_local.create_time,
                'update_by': query_user_local.update_by or '',
                'update_time': query_user_local.update_time,
                'remark': query_user_local.remark or '',
            }
        else:
            # 普通员工：使用字段映射工具
            user_basic_info_dict = FieldMapper.map_employee_to_user_format(query_employee, query_user_local)
        
        # 创建 MappedUser 对象，用于兼容系统框架的数据格式
        class MappedUser:
            """用户数据映射类，支持属性访问"""
            def __init__(self, data: dict):
                if data:
                    for k, v in data.items():
                        setattr(self, k, v)
        
        return MappedUser(user_basic_info_dict) if user_basic_info_dict else None

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: int):
        """
        根据user_id获取用户信息
        使用本地用户表 + 真实员工表 + 部门表

        :param db: orm对象
        :param user_id: 用户id（本地用户表的user_id）
        :return: 当前user_id的用户信息对象
        """
        # 查询本地用户表
        query_user_local = (
            (
                await db.execute(
                    select(SysUserLocal)
                    # 允许查询任何状态的本地账户，只要求启用（enable='1'）
                    .where(SysUserLocal.user_id == user_id, SysUserLocal.enable == '1')
                    .distinct()
                )
            )
            .scalars()
            .first()
        )
        
        if not query_user_local:
            return dict(
                user_basic_info=None,
                user_dept_info=None,
                user_role_info=[],
                user_post_info=[],
                user_menu_info=[],
            )
        
        # 查询员工信息（管理员账户 employee_id=0，不查询员工表）
        query_employee = None
        if query_user_local.employee_id != 0:
            query_employee = (
            (
                await db.execute(
                        select(OaEmployeePrimary)
                        .where(OaEmployeePrimary.id == query_user_local.employee_id)
                        .distinct()
                    )
                )
                .scalars()
                .first()
            )
        
        # 查询部门信息
        query_dept = None
        if query_employee and query_employee.organization_id:
            query_dept = (
                (
                    await db.execute(
                        select(OaDepartment)
                        .where(
                            OaDepartment.id == query_employee.organization_id,
                            OaDepartment.enable == '1',
                    )
                    .distinct()
                )
            )
            .scalars()
            .first()
        )
        
        # 使用字段映射工具转换为系统框架格式
        # 管理员账户特殊处理：employee_id=0 时，使用本地用户表信息
        if query_user_local.employee_id == 0:
            # 管理员账户：使用本地用户表信息，不依赖员工表
            user_basic_info_dict = {
                'user_id': query_user_local.user_id,
                'dept_id': None,  # 管理员没有部门
                'user_name': query_user_local.job_number,
                'nick_name': '系统管理员',
                'user_type': '00',
                'email': '',
                'phonenumber': '',
                'sex': '0',
                'avatar': '',
                'password': query_user_local.password,
                'status': query_user_local.status,
                'del_flag': '0' if query_user_local.enable == '1' else '2',
                'login_ip': query_user_local.login_ip or '',
                'login_date': query_user_local.login_date,
                'pwd_update_date': query_user_local.pwd_update_date,
                'create_by': query_user_local.create_by or '',
                'create_time': query_user_local.create_time,
                'update_by': query_user_local.update_by or '',
                'update_time': query_user_local.update_time,
                'remark': query_user_local.remark or '',
            }
        else:
            # 普通员工：使用字段映射工具
            user_basic_info_dict = FieldMapper.map_employee_to_user_format(query_employee, query_user_local)
        
        # 使用字段映射工具转换部门数据
        dept_info_dict = FieldMapper.map_dept_to_sys_format(query_dept) if query_dept else {}
        
        # 管理员账户判断：user_id=1 或 employee_id=0，并将 admin 属性添加到字典中
        if user_basic_info_dict:
            if query_user_local.employee_id == 0 or user_basic_info_dict.get('user_id') == 1:
                user_basic_info_dict['admin'] = True
            else:
                user_basic_info_dict['admin'] = False
        
        # 创建 MappedUser 和 MappedDept 对象，用于兼容系统框架的数据格式
        # 确保 CamelCaseUtil.transform_result 能够正确处理（因为它有 __dict__ 属性）
        class MappedUser:
            """用户数据映射类，支持属性访问"""
            def __init__(self, data: dict):
                if data:
                    for k, v in data.items():
                        setattr(self, k, v)
        
        class MappedDept:
            """部门数据映射类，支持属性访问"""
            def __init__(self, data: dict):
                if data:
                    for k, v in data.items():
                        setattr(self, k, v)
        
        query_user_basic_info = MappedUser(user_basic_info_dict) if user_basic_info_dict else None
        query_user_dept_info = MappedDept(dept_info_dict) if dept_info_dict else None
        # 查询角色信息（保持不变，使用 sys_user_role 关联）
        query_user_role_info = (
            (
                await db.execute(
                    select(SysRole)
                    .select_from(SysUserLocal)
                    # 角色查询允许任意状态的本地账户，只要求启用
                    .where(SysUserLocal.user_id == user_id, SysUserLocal.enable == '1')
                    .join(SysUserRole, SysUserLocal.user_id == SysUserRole.user_id, isouter=True)
                    .join(
                        SysRole,
                        and_(SysUserRole.role_id == SysRole.role_id, SysRole.status == '0', SysRole.del_flag == '0'),
                    )
                    .distinct()
                )
            )
            .scalars()
            .all()
        )
        # 岗位信息：从 oa_department.rank_id → oa_rank 获取
        query_user_post_info = []
        if query_dept and query_dept.rank_id:
            # 查询职级信息
            query_rank = (
                (
                    await db.execute(
                        select(OaRank)
                        .where(
                            OaRank.id == query_dept.rank_id,
                            OaRank.enable == '1',
                        )
                        .distinct()
                    )
                )
                .scalars()
                .first()
            )
            
            if query_rank:
                # 创建 MappedPost 对象，用于兼容系统框架的返回格式
                class MappedPost:
                    """岗位数据映射类，支持属性访问"""
                    def __init__(self, rank: OaRank):
                        self.post_id = rank.id
                        self.post_name = rank.rank_name
                        self.post_code = rank.rank_code
                        self.post_sort = rank.order_no or 0
                        self.status = '0'  # 系统框架的状态：0正常
                
                query_user_post_info = [MappedPost(query_rank)]
        # 查询菜单信息（使用公共方法，确保逻辑一致）
        # 注意：
        # 1. 只返回角色明确分配的菜单，不自动包含未分配的子菜单
        # 2. 如果子菜单被分配了，会自动包含其父菜单（用于构建树形结构）
        role_id_list = [item.role_id for item in query_user_role_info]
        from module_admin.dao.menu_dao import MenuDao
        query_user_menu_info = await MenuDao._get_user_menus_with_parents(db, user_id, role_id_list)

        results = dict(
            user_basic_info=query_user_basic_info,
            user_dept_info=query_user_dept_info,
            user_role_info=query_user_role_info,
            user_post_info=query_user_post_info,
            user_menu_info=query_user_menu_info,
        )

        return results

    @classmethod
    async def get_user_detail_by_id(cls, db: AsyncSession, user_id: int):
        """
        根据user_id获取用户详细信息
        使用本地用户表 + 真实员工表 + 部门表

        :param db: orm对象
        :param user_id: 用户id（本地用户表的user_id）
        :return: 当前user_id的用户信息对象
        """
        # 复用 get_user_by_id 的逻辑，保持一致性
        return await cls.get_user_by_id(db, user_id)

    @classmethod
    async def get_user_list(
        cls, db: AsyncSession, query_object: UserPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        根据查询参数获取用户列表信息
        从真实员工表开始查询，LEFT JOIN 本地用户表、部门表、职级表和角色表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 用户列表信息对象（返回格式：PageResponseModel 或列表）
        """
        # 构建基础查询条件（从真实员工表开始）
        # 只查询 company_id=2 且 enable='1' 的员工
        # 只显示在职人员：status 为 1（学习期）、2（试用）、3（正式）
        conditions = [
            OaEmployeePrimary.company_id == 2,
            OaEmployeePrimary.enable == '1',
            OaEmployeePrimary.status.in_(['1', '2', '3']),  # 只显示在职人员：学习期、试用、正式
        ]
        
        # 处理部门查询（使用 code LIKE 替代 ancestors）
        # 注意：dept_id=2 表示查询全部员工（不限制部门）
        if query_object.dept_id and query_object.dept_id != 2:
            # 获取当前部门的code
            current_dept = (
                await db.execute(select(OaDepartment).where(OaDepartment.id == query_object.dept_id))
            ).scalars().first()
            
            if current_dept and current_dept.code:
                # 查询当前部门及其子部门
                dept_ids = (
                    await db.execute(
                        select(OaDepartment.id)
                        .where(
                            or_(
                                OaDepartment.id == query_object.dept_id,
                                OaDepartment.code.like(f'{current_dept.code}%')
                            )
                        )
                    )
                ).scalars().all()
                
                if dept_ids:
                    # 通过员工表的 organization_id 关联部门
                    conditions.append(OaEmployeePrimary.organization_id.in_(dept_ids))
                # 如果没有找到部门，不添加条件（返回空结果）
        
        # 处理其他查询条件
        # 兼容旧字段名（user_name, nick_name）和新字段名（job_number, employee_name）
        if query_object.job_number:
            conditions.append(OaEmployeePrimary.job_number.like(f'%{query_object.job_number}%'))
        elif query_object.user_name:
            conditions.append(OaEmployeePrimary.job_number.like(f'%{query_object.user_name}%'))
        
        if query_object.employee_name:
            conditions.append(OaEmployeePrimary.name.like(f'%{query_object.employee_name}%'))
        elif query_object.nick_name:
            conditions.append(OaEmployeePrimary.name.like(f'%{query_object.nick_name}%'))
        
        if query_object.phonenumber:
            conditions.append(OaEmployeePrimary.phone.like(f'%{query_object.phonenumber}%'))
        
        if query_object.rank_id:
            conditions.append(OaEmployeePrimary.rank_id == query_object.rank_id)
        
        if query_object.sex:
            # 真实表的 sex: 1男2女，系统框架: 0男1女2未知
            # 需要转换
            if query_object.sex == '0':  # 系统框架的"男"
                conditions.append(OaEmployeePrimary.sex == '1')  # 真实表的"男"
            elif query_object.sex == '1':  # 系统框架的"女"
                conditions.append(OaEmployeePrimary.sex == '2')  # 真实表的"女"
            # 系统框架的"未知"在真实表中没有对应，不添加条件
        
        # 构建查询：从真实员工表开始，LEFT JOIN 本地用户表、部门表、职级表和角色表
        query = (
            select(OaEmployeePrimary, SysUserLocal, OaDepartment, OaRank, SysRole)
            .where(*conditions)
            .join(
                SysUserLocal,
                and_(
                    OaEmployeePrimary.id == SysUserLocal.employee_id,
                    SysUserLocal.enable == '1',  # 只查询启用的本地用户
                ),
                isouter=True,  # LEFT JOIN，因为可能没有登录账户
            )
            .join(
                OaDepartment,
                and_(
                    OaEmployeePrimary.organization_id == OaDepartment.id,
                    OaDepartment.enable == '1',
                ),
                isouter=True,  # LEFT JOIN，因为可能没有部门
            )
            .join(
                OaRank,
                # 只要能找到对应职级就返回名称，不再按 enable 过滤，避免等级名称为空
                OaEmployeePrimary.rank_id == OaRank.id,
                isouter=True,  # LEFT JOIN，因为可能没有职级
            )
            .join(
                SysUserRole,
                SysUserLocal.user_id == SysUserRole.user_id,
                isouter=True,  # LEFT JOIN，因为可能没有角色
            )
            .join(
                SysRole,
                and_(
                    SysUserRole.role_id == SysRole.role_id,
                    SysRole.status == '0',  # 只查询正常状态的角色
                    SysRole.del_flag == '0',  # 只查询未删除的角色
                ),
                isouter=True,  # LEFT JOIN，因为可能没有角色
            )
        )
        
        if query_object.begin_time and query_object.end_time:
            begin_datetime = datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00))
            end_datetime = datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59))
            # 使用本地用户表的创建时间，如果没有则使用员工表的创建时间
            query = query.where(
                or_(
                    SysUserLocal.create_time.between(begin_datetime, end_datetime),
                    and_(SysUserLocal.user_id.is_(None), OaEmployeePrimary.gmt_create_time.between(begin_datetime, end_datetime))
                )
            )
        
        # 处理 user_id 查询条件（如果传了 user_id，需要通过本地用户表查询）
        if query_object.user_id is not None:
            query = query.where(SysUserLocal.user_id == query_object.user_id)
        
        # 数据权限过滤（需要在JOIN之后，在所有新增查询条件之前）
        # 注意：data_scope_sql 中使用的是空字符串作为 query_alias，'organization_id' 作为 dept_alias
        # 实际查询中，部门信息在 OaEmployeePrimary.organization_id，用户ID在 SysUserLocal.user_id
        # 需要将 data_scope_sql 中的字段名替换为实际的查询路径
        if data_scope_sql:
            # 替换 data_scope_sql 中的字段引用
            # '.organization_id' 或 '.dept_id' -> 'OaEmployeePrimary.organization_id'
            # '.user_id' -> 'SysUserLocal.user_id'
            modified_sql = data_scope_sql.replace('.organization_id', 'OaEmployeePrimary.organization_id')
            modified_sql = modified_sql.replace('.dept_id', 'OaEmployeePrimary.organization_id')
            modified_sql = modified_sql.replace('.user_id', 'SysUserLocal.user_id')
            
            # 修复 hasattr 检查：当 query_alias 是空字符串时，hasattr(, 'field') 会失败
            # 使用正则表达式匹配所有 hasattr(, 'field_name') 模式并替换
            def replace_hasattr(match):
                field_name = match.group(1)
                # 根据字段名决定使用哪个模型
                if field_name in ('organization_id', 'dept_id'):
                    return f"hasattr(OaEmployeePrimary, '{field_name}')"
                elif field_name == 'user_id':
                    return f"hasattr(SysUserLocal, '{field_name}')"
                else:
                    # 默认使用 OaEmployeePrimary（部门相关字段）
                    return f"hasattr(OaEmployeePrimary, '{field_name}')"
            
            # 匹配 hasattr(, 'field_name') 模式
            modified_sql = re.sub(r"hasattr\(\s*,\s*'([^']+)'\)", replace_hasattr, modified_sql)
            
            try:
                data_scope_condition = eval(modified_sql)
                query = query.where(data_scope_condition)
            except Exception as e:
                # 如果替换后的 SQL 无法执行，记录错误但不影响查询
                from utils.log_util import logger
                logger.warning(f'数据权限过滤失败: {str(e)}, SQL: {modified_sql}')
                pass
        
        # 添加额外的查询条件（需要在数据权限过滤之后，确保只在自己权限范围内查询）
        if query_object.status:
            # status 查询条件：使用本地用户表的 status（0正常,1停用）
            if query_object.status == '0':  # 查询正常状态
                query = query.where(SysUserLocal.status == '0')
            elif query_object.status == '1':  # 查询停用状态
                query = query.where(SysUserLocal.status == '1')
        
        # 角色ID查询条件（需要在数据权限过滤之后）
        if query_object.role_id:
            query = query.where(SysRole.role_id == query_object.role_id)
        
        # 排序：使用员工ID排序
        query = query.order_by(OaEmployeePrimary.id).distinct()
        
        # 注意：管理员账户（employee_id=0）不在真实员工表中，所以不会出现在查询结果中
        # 如果需要显示管理员账户，需要在 Service 层单独处理或使用 UNION 查询
        
        # 使用 PageUtil.paginate，保持与框架原有逻辑一致
        # 它会自动调用 CamelCaseUtil.transform_result 转换数据
        # 返回格式：PageResponseModel(rows=[转换后的数据], ...)
        # 对于 select(A, B, C) 多列查询，Row 对象经过 transform_result 后，会转换为列表 [dict1, dict2, dict3]
        # 直接返回，让 Service 层处理转换（保持与原有逻辑一致）
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def add_user_dao(cls, db: AsyncSession, user: UserModel):
        """
        新增用户数据库操作
        注意：用户信息来自真实表，此方法用于创建本地用户记录
        需要先检查真实表中是否存在该员工（通过工号）

        :param db: orm对象
        :param user: 用户对象（包含 userName=工号）
        :return: 新增的本地用户对象
        :raise: 如果真实表中不存在该员工，抛出异常
        """
        # 1. 先检查真实表中是否存在该员工（通过工号）
        employee = (
            await db.execute(
                select(OaEmployeePrimary)
                .where(
                    OaEmployeePrimary.job_number == user.user_name,
                    OaEmployeePrimary.company_id == 2,  # 只处理 company_id=2 的员工
                    OaEmployeePrimary.enable == '1',  # 只处理启用的员工
                )
            )
        ).scalars().first()
        
        if not employee:
            raise ValueError(f'真实表中不存在工号为 {user.user_name} 的员工，无法创建本地用户记录')
        
        # 2. 检查本地用户表中是否已存在该员工
        existing_user = (
            await db.execute(
                select(SysUserLocal)
                .where(SysUserLocal.employee_id == employee.id)
            )
        ).scalars().first()
        
        if existing_user:
            # 如果已存在，更新密码和状态
            if user.password:
                existing_user.password = user.password
            if hasattr(user, 'status') and user.status:
                existing_user.status = user.status
            if hasattr(user, 'update_by') and user.update_by:
                existing_user.update_by = user.update_by
            if hasattr(user, 'update_time') and user.update_time:
                existing_user.update_time = user.update_time
            existing_user.enable = '1'  # 确保启用
            await db.flush()
            return existing_user
        
        # 3. 创建新的本地用户记录
        default_password = user.password if user.password else '123456'
        # 检查密码是否已加密（bcrypt 加密的密码以 $2b$ 开头）
        hashed_password = default_password if default_password.startswith('$2b$') else PwdUtil.get_password_hash(default_password)
        
        local_user = SysUserLocal(
            employee_id=employee.id,
            job_number=employee.job_number,
            password=hashed_password,
            status=user.status if hasattr(user, 'status') and user.status else '0',
            enable='1',
            create_by=user.create_by if hasattr(user, 'create_by') and user.create_by else '',
            create_time=user.create_time if hasattr(user, 'create_time') and user.create_time else datetime.now(),
            update_by=user.update_by if hasattr(user, 'update_by') and user.update_by else '',
            update_time=user.update_time if hasattr(user, 'update_time') and user.update_time else datetime.now(),
        )
        
        db.add(local_user)
        await db.flush()

        return local_user

    @classmethod
    async def edit_user_dao(cls, db: AsyncSession, user: dict):
        """
        编辑用户数据库操作
        注意：现在只用于更新 sys_user_local 表的密码和状态（密码管理）
        用户基本信息来自真实表，不允许修改

        :param db: orm对象
        :param user: 需要更新的用户字典（只包含 password、status、avatar 等允许修改的字段）
        :return: 编辑校验结果
        """
        # 只更新 sys_user_local 表（密码、状态等）
        # 用户基本信息（姓名、部门等）来自真实表，不允许修改
        update_data = {}
        if 'password' in user:
            update_data['password'] = user['password']
        if 'pwd_update_date' in user:
            update_data['pwd_update_date'] = user['pwd_update_date']
        if 'status' in user:
            update_data['status'] = user['status']
        if 'update_by' in user:
            update_data['update_by'] = user['update_by']
        if 'update_time' in user:
            update_data['update_time'] = user['update_time']
        
        if update_data:
            await db.execute(
                update(SysUserLocal)
                .where(SysUserLocal.user_id == user.get('user_id'))
                .values(**update_data)
            )

    @classmethod
    async def delete_user_dao(cls, db: AsyncSession, user: UserModel):
        """
        删除用户数据库操作（软删除）
        注意：现在只用于更新 sys_user_local 表的 enable 字段（禁用账号）
        用户基本信息来自真实表，不允许删除

        :param db: orm对象
        :param user: 用户对象
        :return:
        """
        # 只更新 sys_user_local 表的 enable 字段（禁用账号）
        # 用户基本信息来自真实表，不允许删除
        await db.execute(
            update(SysUserLocal)
            .where(SysUserLocal.user_id == user.user_id)
            .values(
                enable='0',  # 禁用账号
                update_by=user.update_by if hasattr(user, 'update_by') else None,
                update_time=user.update_time if hasattr(user, 'update_time') else datetime.now()
            )
        )

    @classmethod
    async def get_user_role_allocated_list_by_user_id(cls, db: AsyncSession, query_object: UserRoleQueryModel):
        """
        根据用户id获取用户已分配的角色列表信息数据库操作

        :param db: orm对象
        :param query_object: 用户角色查询对象
        :return: 用户已分配的角色列表信息
        """
        allocated_role_list = (
            (
                await db.execute(
                    select(SysRole)
                    .where(
                        SysRole.del_flag == '0',
                        SysRole.role_id != 1,
                        SysRole.role_name == query_object.role_name if query_object.role_name else True,
                        SysRole.role_key == query_object.role_key if query_object.role_key else True,
                        SysRole.role_id.in_(
                            select(SysUserRole.role_id).where(SysUserRole.user_id == query_object.user_id)
                        ),
                    )
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return allocated_role_list

    @classmethod
    async def get_user_role_allocated_list_by_role_id(
        cls, db: AsyncSession, query_object: UserRolePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        根据角色id获取已分配的用户列表信息
        使用真实表 oa_employee_primary + sys_user_local

        :param db: orm对象
        :param query_object: 用户角色查询对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 角色已分配的用户列表信息
        """
        # 构建基础查询条件（从真实员工表开始）
        conditions = [
            OaEmployeePrimary.company_id == 2,
            OaEmployeePrimary.enable == '1',
        ]
        
        # 处理查询条件
        if query_object.user_name:
            conditions.append(OaEmployeePrimary.job_number.like(f'%{query_object.user_name}%'))
        
        if query_object.phonenumber:
            conditions.append(OaEmployeePrimary.phone.like(f'%{query_object.phonenumber}%'))
        
        # 构建查询：从真实员工表开始，LEFT JOIN 本地用户表、部门表和角色关联表
        query = (
            select(OaEmployeePrimary, SysUserLocal, OaDepartment)
            .where(*conditions)
            .join(
                SysUserLocal,
                OaEmployeePrimary.id == SysUserLocal.employee_id,
                isouter=True,
            )
            .join(
                OaDepartment,
                and_(
                    OaEmployeePrimary.organization_id == OaDepartment.id,
                    OaDepartment.enable == '1',
                ),
                isouter=True,
            )
            .join(
                SysUserRole,
                SysUserLocal.user_id == SysUserRole.user_id,
                isouter=True,
            )
            .join(
                SysRole,
                and_(
                    SysUserRole.role_id == SysRole.role_id,
                    SysRole.role_id == query_object.role_id,
                    SysRole.status == '0',
                    SysRole.del_flag == '0',
                ),
                isouter=True,
            )
            .where(
                SysRole.role_id == query_object.role_id,  # 只查询已分配该角色的用户
            )
        )
        
        # 数据权限过滤
        if data_scope_sql:
            modified_sql = data_scope_sql.replace('.organization_id', 'OaEmployeePrimary.organization_id')
            modified_sql = modified_sql.replace('.user_id', 'SysUserLocal.user_id')
            try:
                data_scope_condition = eval(modified_sql)
                query = query.where(data_scope_condition)
            except Exception:
                pass
        
        query = query.order_by(OaEmployeePrimary.id).distinct()
        
        allocated_user_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return allocated_user_list

    @classmethod
    async def get_user_role_unallocated_list_by_role_id(
        cls, db: AsyncSession, query_object: UserRolePageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        根据角色id获取未分配的用户列表信息
        使用真实表 oa_employee_primary + sys_user_local

        :param db: orm对象
        :param query_object: 用户角色查询对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 角色未分配的用户列表信息
        """
        # 构建基础查询条件（从真实员工表开始）
        conditions = [
            OaEmployeePrimary.company_id == 2,
            OaEmployeePrimary.enable == '1',
        ]
        
        # 处理查询条件
        if query_object.user_name:
            conditions.append(OaEmployeePrimary.job_number.like(f'%{query_object.user_name}%'))
        
        if query_object.phonenumber:
            conditions.append(OaEmployeePrimary.phone.like(f'%{query_object.phonenumber}%'))
        
        # 构建查询：从真实员工表开始，LEFT JOIN 本地用户表、部门表和角色关联表
        query = (
            select(OaEmployeePrimary, SysUserLocal, OaDepartment)
            .where(*conditions)
            .join(
                SysUserLocal,
                OaEmployeePrimary.id == SysUserLocal.employee_id,
                isouter=True,
            )
            .join(
                OaDepartment,
                and_(
                    OaEmployeePrimary.organization_id == OaDepartment.id,
                    OaDepartment.enable == '1',
                ),
                isouter=True,
            )
            .join(
                SysUserRole,
                SysUserLocal.user_id == SysUserRole.user_id,
                isouter=True,
            )
            .join(
                SysRole,
                and_(
                    SysUserRole.role_id == SysRole.role_id,
                    SysRole.status == '0',
                    SysRole.del_flag == '0',
                ),
                isouter=True,
            )
            .where(
                # 未分配该角色的用户：角色ID不匹配或为空，且不在已分配列表中
                or_(
                    SysRole.role_id != query_object.role_id,
                    SysRole.role_id.is_(None),
                ),
                ~SysUserLocal.user_id.in_(
                    select(SysUserRole.user_id)
                    .where(SysUserRole.role_id == query_object.role_id)
                ) if query_object.role_id else True,
            )
        )
        
        # 数据权限过滤
        if data_scope_sql:
            modified_sql = data_scope_sql.replace('.organization_id', 'OaEmployeePrimary.organization_id')
            modified_sql = modified_sql.replace('.user_id', 'SysUserLocal.user_id')
            try:
                data_scope_condition = eval(modified_sql)
                query = query.where(data_scope_condition)
            except Exception:
                pass
        
        query = query.order_by(OaEmployeePrimary.id).distinct()
        
        unallocated_user_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return unallocated_user_list

    @classmethod
    async def add_user_role_dao(cls, db: AsyncSession, user_role: UserRoleModel):
        """
        新增用户角色关联信息数据库操作

        :param db: orm对象
        :param user_role: 用户角色关联对象
        :return:
        """
        db_user_role = SysUserRole(**user_role.model_dump())
        db.add(db_user_role)

    @classmethod
    async def delete_user_role_dao(cls, db: AsyncSession, user_role: UserRoleModel):
        """
        删除用户角色关联信息数据库操作

        :param db: orm对象
        :param user_role: 用户角色关联对象
        :return:
        """
        await db.execute(delete(SysUserRole).where(SysUserRole.user_id.in_([user_role.user_id])))

    @classmethod
    async def delete_user_role_by_user_and_role_dao(cls, db: AsyncSession, user_role: UserRoleModel):
        """
        根据用户id及角色id删除用户角色关联信息数据库操作

        :param db: orm对象
        :param user_role: 用户角色关联对象
        :return:
        """
        await db.execute(
            delete(SysUserRole).where(
                SysUserRole.user_id == user_role.user_id if user_role.user_id else True,
                SysUserRole.role_id == user_role.role_id if user_role.role_id else True,
            )
        )

    @classmethod
    async def get_user_role_detail(cls, db: AsyncSession, user_role: UserRoleModel):
        """
        根据用户角色关联获取用户角色关联详细信息

        :param db: orm对象
        :param user_role: 用户角色关联对象
        :return: 用户角色关联信息
        """
        user_role_info = (
            (
                await db.execute(
                    select(SysUserRole)
                    .where(SysUserRole.user_id == user_role.user_id, SysUserRole.role_id == user_role.role_id)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return user_role_info

    @classmethod
    async def get_user_dept_info(cls, db: AsyncSession, dept_id: int):
        """
        根据部门id获取部门信息
        使用真实表 oa_department
        """
        dept_basic_info = (
            (
                await db.execute(
                    select(OaDepartment).where(
                        OaDepartment.id == dept_id, 
                        OaDepartment.status == '0', 
                        OaDepartment.enable == '1'
                    )
                )
            )
            .scalars()
            .first()
        )
        return dept_basic_info
