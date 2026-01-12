from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.service.login_service import LoginService
from module_admin.service.sync_service import SyncService
from config.get_db import get_db
from utils.response_util import ResponseUtil


syncController = APIRouter(prefix='/system/sync', dependencies=[Depends(LoginService.get_current_user)])


@syncController.post(
    '/employees',
    dependencies=[Depends(CheckUserInterfaceAuth('system:sync:employees'))],
)
@Log(title='数据同步', business_type=BusinessType.UPDATE)
async def sync_all_employees(
    company_id: int = Query(default=2, description='公司ID'),
    default_password: str = Query(default=None, description='默认密码（新增用户时使用）'),
    sync_deleted: bool = Query(default=True, description='是否同步删除'),
    query_db: AsyncSession = Depends(get_db),
) -> CrudResponseModel:
    """
    同步所有员工数据到本地用户表
    
    :param company_id: 公司ID，默认2
    :param default_password: 默认密码（新增用户时使用，如果不提供则使用默认密码123456）
    :param sync_deleted: 是否同步删除（软删除真实表中不存在的用户），默认True
    :param query_db: 数据库会话
    :return: 同步结果
    """
    result = await SyncService.sync_employees_services(
        query_db=query_db,
        company_id=company_id,
        default_password=default_password,
        sync_deleted=sync_deleted,
    )
    return ResponseUtil.success(data=result, message=result.message)


@syncController.post(
    '/employee/{employee_id}',
    dependencies=[Depends(CheckUserInterfaceAuth('system:sync:employee'))],
)
@Log(title='数据同步', business_type=BusinessType.UPDATE)
async def sync_single_employee(
    employee_id: int,
    company_id: int = Query(default=2, description='公司ID'),
    default_password: str = Query(default=None, description='默认密码（新增用户时使用）'),
    query_db: AsyncSession = Depends(get_db),
) -> CrudResponseModel:
    """
    同步单个员工数据到本地用户表
    
    :param employee_id: 员工ID
    :param company_id: 公司ID，默认2
    :param default_password: 默认密码（新增用户时使用）
    :param query_db: 数据库会话
    :return: 同步结果
    """
    result = await SyncService.sync_single_employee_services(
        query_db=query_db,
        employee_id=employee_id,
        company_id=company_id,
        default_password=default_password,
    )
    return ResponseUtil.success(data=result, message=result.message)
