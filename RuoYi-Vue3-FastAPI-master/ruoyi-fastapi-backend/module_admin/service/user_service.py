from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from module_admin.entity.do.oa_rank_do import OaRank
from utils.field_mapper import FieldMapper
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.dao.user_dao import UserDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.user_vo import (
    AddUserModel,
    CrudUserRoleModel,
    CurrentUserModel,
    DeleteUserModel,
    EditUserModel,
    ResetUserModel,
    SelectedRoleModel,
    UserDetailModel,
    UserInfoModel,
    UserModel,
    UserPageQueryModel,
    UserProfileModel,
    UserRoleModel,
    UserRoleQueryModel,
    UserRoleResponseModel,
)
from module_admin.service.dept_service import DeptService
from module_admin.service.role_service import RoleService
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil
from utils.page_util import PageResponseModel
from utils.pwd_util import PwdUtil


class UserService:
    """
    用户管理模块服务层
    """

    @staticmethod
    def _convert_user_list_rows(rows: list) -> list:
        """
        将用户列表查询结果转换为系统框架格式
        处理角色聚合、字段名称转换等
        
        :param rows: 查询结果行列表（每个 row 是 [employee_dict, user_local_dict, dept_dict, rank_dict, role_dict]）
        :return: 转换后的用户列表
        """
        from utils.common_util import CamelCaseUtil, SnakeCaseUtil
        from utils.field_mapper import FieldMapper
        
        # 由于一个用户可能有多个角色，JOIN 会产生多行，需要按 user_id 分组聚合
        user_data_map = {}  # {user_id: {user_data, roles: []}}
        
        for row in rows:
            # row 是列表格式：[employee_dict, user_local_dict, dept_dict, rank_dict, role_dict]
            # 查询顺序：OaEmployeePrimary, SysUserLocal, OaDepartment, OaRank, SysRole
            if isinstance(row, list):
                employee_dict = row[0] if len(row) > 0 else None
                user_local_dict = row[1] if len(row) > 1 else None
                dept_dict = row[2] if len(row) > 2 else None
                rank_dict = row[3] if len(row) > 3 else None
                role_dict = row[4] if len(row) > 4 else None
            else:
                # Row 对象，通过索引访问
                employee_dict = row[0] if hasattr(row, '__getitem__') and len(row) > 0 else None
                user_local_dict = row[1] if hasattr(row, '__getitem__') and len(row) > 1 else None
                dept_dict = row[2] if hasattr(row, '__getitem__') and len(row) > 2 else None
                rank_dict = row[3] if hasattr(row, '__getitem__') and len(row) > 3 else None
                role_dict = row[4] if hasattr(row, '__getitem__') and len(row) > 4 else None
            
            # 转换为下划线格式以便处理
            employee_snake = SnakeCaseUtil.transform_result(employee_dict) if isinstance(employee_dict, dict) and employee_dict else None
            user_local_snake = SnakeCaseUtil.transform_result(user_local_dict) if isinstance(user_local_dict, dict) and user_local_dict else {}
            dept_snake = SnakeCaseUtil.transform_result(dept_dict) if isinstance(dept_dict, dict) and dept_dict else None
            rank_snake = SnakeCaseUtil.transform_result(rank_dict) if isinstance(rank_dict, dict) and rank_dict else None
            role_snake = SnakeCaseUtil.transform_result(role_dict) if isinstance(role_dict, dict) and role_dict else None
            
            # 获取 user_id（用于分组）
            user_id = user_local_snake.get('user_id') if isinstance(user_local_snake, dict) else None
            
            if not employee_snake or not user_id:
                continue
            
            # 如果该用户还没有处理过，初始化用户数据
            if user_id not in user_data_map:
                # 转换为系统框架格式
                mapped_user_dict = FieldMapper.map_employee_to_user_format(employee_snake, user_local_snake)
                mapped_dept_dict = FieldMapper.map_dept_to_sys_format(dept_snake) if dept_snake else {}
                
                # 转换为 camelCase
                user_camel = CamelCaseUtil.transform_result(mapped_user_dict)
                dept_camel = CamelCaseUtil.transform_result(mapped_dept_dict) if mapped_dept_dict else {}
                
                # 添加岗位信息
                rank_camel = CamelCaseUtil.transform_result(rank_snake) if rank_snake else {}
                user_camel['rankName'] = rank_camel.get('rankName') if rank_camel else None
                user_camel['rankId'] = rank_camel.get('id') if rank_camel else None
                
                # 修改字段名称
                if 'userName' in user_camel:
                    user_camel['jobNumber'] = user_camel.pop('userName')
                if 'nickName' in user_camel:
                    user_camel['employeeName'] = user_camel.pop('nickName')
                
                # 移除 createTime 字段
                user_camel.pop('createTime', None)
                
                # 添加编制显示格式（deptName 已经是"部门名称-deptID"格式，直接使用）
                if dept_camel and dept_camel.get('deptName'):
                    dept_camel['deptNameWithId'] = dept_camel.get('deptName')
                
                user_data_map[user_id] = {
                    'user_data': {**user_camel, 'dept': dept_camel},
                    'roles': []
                }
            
            # 聚合角色信息
            if role_snake and role_snake.get('role_id'):
                role_camel = CamelCaseUtil.transform_result(role_snake)
                role_obj = {
                    'roleId': role_camel.get('roleId'),
                    'roleName': role_camel.get('roleName')
                }
                # 避免重复添加相同角色
                existing_role = next((r for r in user_data_map[user_id]['roles'] if r.get('roleId') == role_obj.get('roleId')), None)
                if not existing_role:
                    user_data_map[user_id]['roles'].append(role_obj)
        
        # 构建最终返回数据
        converted_rows = []
        for user_id, data in user_data_map.items():
            user_data = data['user_data']
            roles = data['roles']
            
            # 清洗角色信息，过滤无效角色
            valid_roles = [r for r in roles if r.get('roleId') is not None and r.get('roleName')]
            user_data['roles'] = valid_roles
            # 生成角色名称字符串，过滤掉 None 值
            role_names = [r.get('roleName') for r in valid_roles if r.get('roleName')]
            user_data['roleNames'] = ', '.join(role_names) if role_names else '未配置'
            
            converted_rows.append(user_data)
        
        return converted_rows

    @classmethod
    async def get_user_list_services(
        cls, query_db: AsyncSession, query_object: UserPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        获取用户列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 用户列表信息对象
        """
        query_result = await UserDao.get_user_list(query_db, query_object, data_scope_sql, is_page)
        
        # 处理查询结果（分页和非分页使用相同的转换逻辑）
        converted_rows = cls._convert_user_list_rows(query_result.rows if is_page else query_result)
        
        if is_page:
            # 返回分页结果，保持原有格式
            return PageResponseModel(
                **{
                    **query_result.model_dump(by_alias=True),
                    'rows': converted_rows,
                }
            )
        else:
            # 返回非分页结果
            return converted_rows

    @classmethod
    async def check_user_allowed_services(cls, check_user: UserModel):
        """
        校验用户是否允许操作service

        :param check_user: 用户信息
        :return: 校验结果
        """
        if check_user.admin:
            raise ServiceException(message='不允许操作超级管理员用户')
        else:
            return CrudResponseModel(is_success=True, message='校验通过')

    @classmethod
    async def check_user_data_scope_services(cls, query_db: AsyncSession, user_id: int, data_scope_sql: str):
        """
        校验用户数据权限service

        :param query_db: orm对象
        :param user_id: 用户id
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 校验结果
        """
        # 恢复原有逻辑：沿用用户列表查询校验数据权限
        users = await UserDao.get_user_list(query_db, UserPageQueryModel(userId=user_id), data_scope_sql, is_page=False)
        if users:
            return CrudResponseModel(is_success=True, message='校验通过')
        else:
            raise ServiceException(message='没有权限访问用户数据')

    @classmethod
    async def check_user_name_unique_services(cls, query_db: AsyncSession, page_object: UserModel):
        """
        校验用户名是否唯一service

        :param query_db: orm对象
        :param page_object: 用户对象
        :return: 校验结果
        """
        user_id = -1 if page_object.user_id is None else page_object.user_id
        user = await UserDao.get_user_by_info(query_db, UserModel(userName=page_object.user_name))
        if user and user.user_id != user_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def check_phonenumber_unique_services(cls, query_db: AsyncSession, page_object: UserModel):
        """
        校验用户手机号是否唯一service

        :param query_db: orm对象
        :param page_object: 用户对象
        :return: 校验结果
        """
        user_id = -1 if page_object.user_id is None else page_object.user_id
        user = await UserDao.get_user_by_info(query_db, UserModel(phonenumber=page_object.phonenumber))
        if user and user.user_id != user_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def check_email_unique_services(cls, query_db: AsyncSession, page_object: UserModel):
        """
        校验用户邮箱是否唯一service

        :param query_db: orm对象
        :param page_object: 用户对象
        :return: 校验结果
        """
        user_id = -1 if page_object.user_id is None else page_object.user_id
        user = await UserDao.get_user_by_info(query_db, UserModel(email=page_object.email))
        if user and user.user_id != user_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_user_services(cls, query_db: AsyncSession, page_object: AddUserModel):
        """
        新增用户信息service

        :param query_db: orm对象
        :param page_object: 新增用户对象
        :return: 新增用户校验结果
        """
        add_user = UserModel(**page_object.model_dump(by_alias=True))
        if not await cls.check_user_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增用户{page_object.user_name}失败，登录账号已存在')
        elif page_object.phonenumber and not await cls.check_phonenumber_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增用户{page_object.user_name}失败，手机号码已存在')
        elif page_object.email and not await cls.check_email_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增用户{page_object.user_name}失败，邮箱账号已存在')
        else:
            try:
                add_result = await UserDao.add_user_dao(query_db, add_user)
                user_id = add_result.user_id
                if page_object.role_ids:
                    for role in page_object.role_ids:
                        await UserDao.add_user_role_dao(query_db, UserRoleModel(userId=user_id, roleId=role))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='新增成功')
            except Exception as e:
                await query_db.rollback()
                raise e

    @classmethod
    async def edit_user_services(cls, query_db: AsyncSession, page_object: EditUserModel):
        """
        编辑用户信息service
        注意：现在只用于更新 sys_user_local 表的密码和状态（密码管理）
        用户基本信息来自真实表，不允许修改

        :param query_db: orm对象
        :param page_object: 编辑用户对象（只允许 type='pwd'、'status'、'avatar'）
        :return: 编辑用户校验结果
        """
        # 只允许修改密码、状态、头像（这些是本地用户表的字段）
        # 不允许修改用户基本信息（姓名、部门等，这些来自真实表）
        if page_object.type not in ['pwd', 'status', 'avatar']:
            raise ServiceException(message='不允许修改用户基本信息，用户信息来自真实表（只读）')
        
        edit_user = page_object.model_dump(exclude_unset=True, exclude={'admin'})
        del edit_user['type']
        
        # 检查用户是否存在（通过本地用户表）
        user_info = await cls.user_detail_services(query_db, edit_user.get('user_id'))
        if user_info.data and user_info.data.user_id:
            try:
                # 只更新 sys_user_local 表（密码、状态等）
                await UserDao.edit_user_dao(query_db, edit_user)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='用户不存在')

    @classmethod
    async def delete_user_services(cls, query_db: AsyncSession, page_object: DeleteUserModel):
        """
        删除用户信息service

        :param query_db: orm对象
        :param page_object: 删除用户对象
        :return: 删除用户校验结果
        """
        if page_object.user_ids:
            user_id_list = page_object.user_ids.split(',')
            try:
                for user_id in user_id_list:
                    user_id_dict = dict(
                        userId=user_id, updateBy=page_object.update_by, updateTime=page_object.update_time
                    )
                    await UserDao.delete_user_role_dao(query_db, UserRoleModel(**user_id_dict))
                    await UserDao.delete_user_dao(query_db, UserModel(**user_id_dict))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入用户id为空')

    @classmethod
    async def user_detail_services(cls, query_db: AsyncSession, user_id: Union[int, str]):
        """
        获取用户详细信息service

        :param query_db: orm对象
        :param user_id: 用户id
        :return: 用户id对应的信息
        """
        # 从 oa_rank 获取职级列表（作为岗位列表显示，只读）
        rank_query = select(OaRank).where(OaRank.enable == '1').order_by(OaRank.order_no)
        rank_list = (await query_db.execute(rank_query)).scalars().all()
        # 转换为岗位格式（使用字段映射工具）
        posts = [FieldMapper.map_rank_to_post_format(rank) for rank in rank_list]
        roles = await RoleService.get_role_select_option_services(query_db)
        if user_id != '':
            query_user = await UserDao.get_user_detail_by_id(query_db, user_id=user_id)
            post_ids = ','.join([str(row.post_id) for row in query_user.get('user_post_info')])
            post_ids_list = [row.post_id for row in query_user.get('user_post_info')]
            role_ids = ','.join([str(row.role_id) for row in query_user.get('user_role_info')])
            role_ids_list = [row.role_id for row in query_user.get('user_role_info')]

            return UserDetailModel(
                data=UserInfoModel(
                    **CamelCaseUtil.transform_result(query_user.get('user_basic_info')),
                    postIds=post_ids,
                    roleIds=role_ids,
                    dept=CamelCaseUtil.transform_result(query_user.get('user_dept_info')),
                    role=CamelCaseUtil.transform_result(query_user.get('user_role_info')),
                ),
                postIds=post_ids_list,
                posts=posts,
                roleIds=role_ids_list,
                roles=roles,
            )

        return UserDetailModel(posts=posts, roles=roles)

    @classmethod
    async def user_profile_services(cls, query_db: AsyncSession, user_id: int):
        """
        获取用户个人详细信息service

        :param query_db: orm对象
        :param user_id: 用户id
        :return: 用户id对应的信息
        """
        query_user = await UserDao.get_user_detail_by_id(query_db, user_id=user_id)
        post_ids = ','.join([str(row.post_id) for row in query_user.get('user_post_info')])
        post_group = ','.join([row.post_name for row in query_user.get('user_post_info')])
        role_ids = ','.join([str(row.role_id) for row in query_user.get('user_role_info')])
        role_group = ','.join([row.role_name for row in query_user.get('user_role_info')])

        return UserProfileModel(
            data=UserInfoModel(
                **CamelCaseUtil.transform_result(query_user.get('user_basic_info')),
                postIds=post_ids,
                roleIds=role_ids,
                dept=CamelCaseUtil.transform_result(query_user.get('user_dept_info')),
                role=CamelCaseUtil.transform_result(query_user.get('user_role_info')),
            ),
            postGroup=post_group,
            roleGroup=role_group,
        )

    @classmethod
    async def reset_user_services(cls, query_db: AsyncSession, page_object: ResetUserModel):
        """
        重置用户密码service

        :param query_db: orm对象
        :param page_object: 重置用户对象
        :return: 重置用户校验结果
        """
        reset_user = page_object.model_dump(exclude_unset=True, exclude={'admin'})
        if page_object.old_password:
            user = (await UserDao.get_user_detail_by_id(query_db, user_id=page_object.user_id)).get('user_basic_info')
            if not PwdUtil.verify_password(page_object.old_password, user.password):
                raise ServiceException(message='修改密码失败，旧密码错误')
            elif PwdUtil.verify_password(page_object.password, user.password):
                raise ServiceException(message='新密码不能与旧密码相同')
            else:
                del reset_user['old_password']
        if page_object.sms_code and page_object.session_id:
            del reset_user['sms_code']
            del reset_user['session_id']
        try:
            reset_user['password'] = PwdUtil.get_password_hash(page_object.password)
            await UserDao.edit_user_dao(query_db, reset_user)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='重置成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @staticmethod
    async def export_user_list_services(user_list: List):
        """
        导出用户信息service

        :param user_list: 用户信息列表
        :return: 用户信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'userId': '用户编号',
            'userName': '用户名称',
            'nickName': '用户昵称',
            'deptName': '部门',
            'email': '邮箱地址',
            'phonenumber': '手机号码',
            'sex': '性别',
            'status': '状态',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }

        for item in user_list:
            item['deptName'] = item.get('dept').get('deptName')
            if item.get('status') == '0':
                item['status'] = '正常'
            else:
                item['status'] = '停用'
            if item.get('sex') == '0':
                item['sex'] = '男'
            elif item.get('sex') == '1':
                item['sex'] = '女'
            else:
                item['sex'] = '未知'
        binary_data = ExcelUtil.export_list2excel(user_list, mapping_dict)

        return binary_data

    @classmethod
    async def get_user_role_allocated_list_services(cls, query_db: AsyncSession, page_object: UserRoleQueryModel):
        """
        根据用户id获取已分配角色列表

        :param query_db: orm对象
        :param page_object: 用户关联角色对象
        :return: 已分配角色列表
        """
        query_user = await UserDao.get_user_detail_by_id(query_db, page_object.user_id)
        post_ids = ','.join([str(row.post_id) for row in query_user.get('user_post_info')])
        role_ids = ','.join([str(row.role_id) for row in query_user.get('user_role_info')])
        user = UserInfoModel(
            **CamelCaseUtil.transform_result(query_user.get('user_basic_info')),
            postIds=post_ids,
            roleIds=role_ids,
            dept=CamelCaseUtil.transform_result(query_user.get('user_dept_info')),
            role=CamelCaseUtil.transform_result(query_user.get('user_role_info')),
        )
        query_role_list = [
            SelectedRoleModel(**row) for row in await RoleService.get_role_select_option_services(query_db)
        ]
        for model_a in query_role_list:
            for model_b in user.role:
                if model_a.role_id == model_b.role_id:
                    model_a.flag = True
        result = UserRoleResponseModel(roles=query_role_list, user=user)

        return result

    @classmethod
    async def add_user_role_services(cls, query_db: AsyncSession, page_object: CrudUserRoleModel):
        """
        新增用户关联角色信息service

        :param query_db: orm对象
        :param page_object: 新增用户关联角色对象
        :return: 新增用户关联角色校验结果
        """
        if page_object.user_id and page_object.role_ids:
            role_id_list = page_object.role_ids.split(',')
            try:
                await UserDao.delete_user_role_by_user_and_role_dao(query_db, UserRoleModel(userId=page_object.user_id))
                for role_id in role_id_list:
                    await UserDao.add_user_role_dao(query_db, UserRoleModel(userId=page_object.user_id, roleId=role_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='分配成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        elif page_object.user_id and not page_object.role_ids:
            try:
                await UserDao.delete_user_role_by_user_and_role_dao(query_db, UserRoleModel(userId=page_object.user_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='分配成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        elif page_object.user_ids and page_object.role_id:
            user_id_list = page_object.user_ids.split(',')
            try:
                for user_id in user_id_list:
                    user_role = await cls.detail_user_role_services(
                        query_db, UserRoleModel(userId=user_id, roleId=page_object.role_id)
                    )
                    if user_role:
                        continue
                    else:
                        await UserDao.add_user_role_dao(
                            query_db, UserRoleModel(userId=user_id, roleId=page_object.role_id)
                        )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='新增成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='不满足新增条件')

    @classmethod
    async def delete_user_role_services(cls, query_db: AsyncSession, page_object: CrudUserRoleModel):
        """
        删除用户关联角色信息service

        :param query_db: orm对象
        :param page_object: 删除用户关联角色对象
        :return: 删除用户关联角色校验结果
        """
        if (page_object.user_id and page_object.role_id) or (page_object.user_ids and page_object.role_id):
            if page_object.user_id and page_object.role_id:
                try:
                    await UserDao.delete_user_role_by_user_and_role_dao(
                        query_db, UserRoleModel(userId=page_object.user_id, roleId=page_object.role_id)
                    )
                    await query_db.commit()
                    return CrudResponseModel(is_success=True, message='删除成功')
                except Exception as e:
                    await query_db.rollback()
                    raise e
            elif page_object.user_ids and page_object.role_id:
                user_id_list = page_object.user_ids.split(',')
                try:
                    for user_id in user_id_list:
                        await UserDao.delete_user_role_by_user_and_role_dao(
                            query_db, UserRoleModel(userId=user_id, roleId=page_object.role_id)
                        )
                    await query_db.commit()
                    return CrudResponseModel(is_success=True, message='删除成功')
                except Exception as e:
                    await query_db.rollback()
                    raise e
            else:
                raise ServiceException(message='不满足删除条件')
        else:
            raise ServiceException(message='传入用户角色关联信息为空')

    @classmethod
    async def detail_user_role_services(cls, query_db: AsyncSession, page_object: UserRoleModel):
        """
        获取用户关联角色详细信息service

        :param query_db: orm对象
        :param page_object: 用户关联角色对象
        :return: 用户关联角色详细信息
        """
        user_role = await UserDao.get_user_role_detail(query_db, page_object)

        return user_role
