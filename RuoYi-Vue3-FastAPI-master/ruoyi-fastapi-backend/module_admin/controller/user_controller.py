import os
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal, Optional, Union
from pydantic_validation_decorator import ValidateFields
from config.get_db import get_db
from config.enums import BusinessType
from config.env import UploadConfig
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from exceptions.exception import ServiceException
from module_admin.entity.vo.dept_vo import DeptModel
from module_admin.entity.vo.user_vo import (
    AddUserModel,
    CrudUserRoleModel,
    CurrentUserModel,
    DeleteUserModel,
    EditUserModel,
    ResetPasswordModel,
    ResetUserModel,
    UserDetailModel,
    UserInfoModel,
    UserModel,
    UserPageQueryModel,
    UserProfileModel,
    UserRoleQueryModel,
    UserRoleResponseModel,
)
from module_admin.service.login_service import LoginService
from module_admin.service.user_service import UserService
from module_admin.service.role_service import RoleService
from module_admin.service.dept_service import DeptService
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.pwd_util import PwdUtil
from utils.response_util import ResponseUtil
from utils.upload_util import UploadUtil


userController = APIRouter(prefix='/system/user', dependencies=[Depends(LoginService.get_current_user)])


@userController.get('/deptTree', dependencies=[Depends(CheckUserInterfaceAuth('system:user:list'))])
async def get_system_dept_tree(
    request: Request, query_db: AsyncSession = Depends(get_db), data_scope_sql: str = Depends(GetDataScope('OaDepartment', dept_alias='id'))
):
    dept_query_result = await DeptService.get_dept_tree_services(query_db, DeptModel(**{}), data_scope_sql)
    logger.info('获取成功')

    return ResponseUtil.success(data=dept_query_result)


@userController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:user:list'))]
)
async def get_system_user_list(
    request: Request,
    user_page_query: UserPageQueryModel = Depends(UserPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    # 注意：使用空字符串作为 query_alias，因为实际查询中需要通过 OaEmployeePrimary.organization_id 访问部门
    data_scope_sql: str = Depends(GetDataScope('', dept_alias='organization_id')),
):
    # 获取分页数据
    user_page_query_result = await UserService.get_user_list_services(
        query_db, user_page_query, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=user_page_query_result)
# 保留的接口：
# - PUT /system/user/resetPwd - 重置密码（密码管理，允许）
# - PUT /system/user/changeStatus - 修改状态（本地用户表状态，允许）


@userController.put('/resetPwd', dependencies=[Depends(CheckUserInterfaceAuth('system:user:resetPwd'))])
@Log(title='用户管理', business_type=BusinessType.UPDATE)
async def reset_system_user_pwd(
    request: Request,
    reset_user: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('', user_alias='user_id')),
):
    await UserService.check_user_allowed_services(reset_user)
    if not current_user.user.admin:
        await UserService.check_user_data_scope_services(query_db, reset_user.user_id, data_scope_sql)
    edit_user = EditUserModel(
        userId=reset_user.user_id,
        password=PwdUtil.get_password_hash(reset_user.password),
        pwdUpdateDate=datetime.now(),
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
        type='pwd',
    )
    edit_user_result = await UserService.edit_user_services(query_db, edit_user)
    logger.info(edit_user_result.message)

    return ResponseUtil.success(msg=edit_user_result.message)


@userController.put('/changeStatus', dependencies=[Depends(CheckUserInterfaceAuth('system:user:edit'))])
@Log(title='用户管理', business_type=BusinessType.UPDATE)
async def change_system_user_status(
    request: Request,
    change_user: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('', user_alias='user_id')),
):
    # 禁止用户修改自己的状态（避免误操作导致无法登录）
    if change_user.user_id == current_user.user.user_id:
        raise ServiceException(message='不允许修改自己的状态')
    
    await UserService.check_user_allowed_services(change_user)
    if not current_user.user.admin:
        await UserService.check_user_data_scope_services(query_db, change_user.user_id, data_scope_sql)
    edit_user = EditUserModel(
        userId=change_user.user_id,
        status=change_user.status,
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
        type='status',
    )
    edit_user_result = await UserService.edit_user_services(query_db, edit_user)
    logger.info(edit_user_result.message)

    return ResponseUtil.success(msg=edit_user_result.message)


@userController.get('/profile', response_model=UserProfileModel)
async def query_detail_system_user_profile(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    profile_user_result = await UserService.user_profile_services(query_db, current_user.user.user_id)
    logger.info(f'获取user_id为{current_user.user.user_id}的信息成功')

    return ResponseUtil.success(model_content=profile_user_result)


@userController.get(
    '/{user_id}', response_model=UserDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('system:user:query'))]
)
@userController.get(
    '/', response_model=UserDetailModel, dependencies=[Depends(CheckUserInterfaceAuth('system:user:query'))]
)
async def query_detail_system_user(
    request: Request,
    user_id: Optional[Union[int, Literal['']]] = '',
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('', user_alias='user_id')),
):
    if user_id and not current_user.user.admin:
        await UserService.check_user_data_scope_services(query_db, user_id, data_scope_sql)
    detail_user_result = await UserService.user_detail_services(query_db, user_id)
    logger.info(f'获取user_id为{user_id}的信息成功')

    return ResponseUtil.success(model_content=detail_user_result)


@userController.post('/profile/avatar')
@Log(title='个人信息', business_type=BusinessType.UPDATE)
async def change_system_user_profile_avatar(
    request: Request,
    avatarfile: bytes = File(),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    if avatarfile:
        relative_path = (
            f'avatar/{datetime.now().strftime("%Y")}/{datetime.now().strftime("%m")}/{datetime.now().strftime("%d")}'
        )
        dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass
        avatar_name = f'avatar_{datetime.now().strftime("%Y%m%d%H%M%S")}{UploadConfig.UPLOAD_MACHINE}{UploadUtil.generate_random_number()}.png'
        avatar_path = os.path.join(dir_path, avatar_name)
        with open(avatar_path, 'wb') as f:
            f.write(avatarfile)
        edit_user = EditUserModel(
            userId=current_user.user.user_id,
            avatar=f'{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{avatar_name}',
            updateBy=current_user.user.user_name,
            updateTime=datetime.now(),
            type='avatar',
        )
        edit_user_result = await UserService.edit_user_services(query_db, edit_user)
        logger.info(edit_user_result.message)

        return ResponseUtil.success(dict_content={'imgUrl': edit_user.avatar}, msg=edit_user_result.message)
    return ResponseUtil.failure(msg='上传图片异常，请联系管理员')


@userController.put('/profile')
@Log(title='个人信息', business_type=BusinessType.UPDATE)
async def change_system_user_profile_info(
    request: Request,
    user_info: UserInfoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_user = EditUserModel(
        **user_info.model_dump(exclude_unset=True, by_alias=True, exclude={'role_ids', 'post_ids'}),
        userId=current_user.user.user_id,
        userName=current_user.user.user_name,
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
        roleIds=current_user.user.role_ids.split(',') if current_user.user.role_ids else [],
        postIds=current_user.user.post_ids.split(',') if current_user.user.post_ids else [],
        role=current_user.user.role,
    )
    edit_user_result = await UserService.edit_user_services(query_db, edit_user)
    logger.info(edit_user_result.message)

    return ResponseUtil.success(msg=edit_user_result.message)


@userController.put('/profile/updatePwd')
@Log(title='个人信息', business_type=BusinessType.UPDATE)
async def reset_system_user_password(
    request: Request,
    reset_password: ResetPasswordModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    reset_user = ResetUserModel(
        userId=current_user.user.user_id,
        oldPassword=reset_password.old_password,
        password=reset_password.new_password,
        pwdUpdateDate=datetime.now(),
        updateBy=current_user.user.user_name,
        updateTime=datetime.now(),
    )
    reset_user_result = await UserService.reset_user_services(query_db, reset_user)
    logger.info(reset_user_result.message)

    return ResponseUtil.success(msg=reset_user_result.message)


@userController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('system:user:export'))])
@Log(title='用户管理', business_type=BusinessType.EXPORT)
async def export_system_user_list(
    request: Request,
    user_page_query: UserPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('', user_alias='user_id')),
):
    # 获取全量数据
    user_query_result = await UserService.get_user_list_services(
        query_db, user_page_query, data_scope_sql, is_page=False
    )
    user_export_result = await UserService.export_user_list_services(user_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(user_export_result))


@userController.get(
    '/authRole/{user_id}',
    response_model=UserRoleResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('system:user:query'))],
)
async def get_system_allocated_role_list(request: Request, user_id: int, query_db: AsyncSession = Depends(get_db)):
    user_role_query = UserRoleQueryModel(userId=user_id)
    user_role_allocated_query_result = await UserService.get_user_role_allocated_list_services(
        query_db, user_role_query
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=user_role_allocated_query_result)


@userController.put(
    '/authRole',
    response_model=UserRoleResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('system:user:edit'))],
)
@Log(title='用户管理', business_type=BusinessType.GRANT)
async def update_system_role_user(
    request: Request,
    user_id: int = Query(alias='userId'),
    role_ids: str = Query(alias='roleIds'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    user_data_scope_sql: str = Depends(GetDataScope('', user_alias='user_id')),
    role_data_scope_sql: str = Depends(GetDataScope('OaDepartment')),
):
    if not current_user.user.admin:
        await UserService.check_user_data_scope_services(query_db, user_id, user_data_scope_sql)
        await RoleService.check_role_data_scope_services(query_db, role_ids, role_data_scope_sql)
    add_user_role_result = await UserService.add_user_role_services(
        query_db, CrudUserRoleModel(userId=user_id, roleIds=role_ids)
    )
    logger.info(add_user_role_result.message)

    return ResponseUtil.success(msg=add_user_role_result.message)
