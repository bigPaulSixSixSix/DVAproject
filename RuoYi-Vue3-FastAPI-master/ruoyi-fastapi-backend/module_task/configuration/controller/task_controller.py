import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckWorkbenchMenuAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_task.entity.vo.task_vo import (
    DeleteTaskConfigModel,
    TaskConfigModel,
    TaskConfigPageQueryModel,
    TaskConfigPayload,
)
from module_task.configuration.service.task_service import TaskService
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil

# 测试数据存储目录
TEST_DATA_DIR = "vf_admin/task_test_data"


def ensure_test_data_dir():
    """确保测试数据目录存在"""
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR)
        logger.info(f'创建测试数据目录: {TEST_DATA_DIR}')


def save_test_data_to_file(task_data: dict, current_user: str) -> str:
    """
    将测试数据保存为JSON文件
    
    :param task_data: 任务配置数据
    :param current_user: 当前用户
    :return: 保存的文件路径
    """
    ensure_test_data_dir()
    
    # 生成文件名：任务名称_用户名_时间戳.json
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 精确到毫秒
    task_name = task_data.get('taskName', 'unnamed')
    # 清理文件名中的特殊字符
    safe_task_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_task_name = safe_task_name.replace(' ', '_')[:50]  # 限制长度
    
    filename = f'{safe_task_name}_{current_user}_{timestamp}.json'
    filepath = os.path.join(TEST_DATA_DIR, filename)
    
    # 保存原始JSON数据
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f'测试数据已保存到: {filepath}')
    return filepath


taskController = APIRouter(prefix='/task', dependencies=[Depends(LoginService.get_current_user)])


@taskController.post('/save', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def save_task_config(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    保存任务配置（仅保存，不生成任务）
    统一处理流程：结构校验 -> 内容校验 -> 数据持久化
    适用于：已生成任务的项目中临时保存任务配置，等待确认后再生成
    """
    logger.info(f'收到任务配置保存请求，用户：{current_user.user.user_name}')

    # 读取原始请求体
    raw_body = await request.body()

    # 保存测试数据，便于排查问题
    try:
        parsed_body = json.loads(raw_body.decode('utf-8'))
        saved_path = save_test_data_to_file(parsed_body, current_user.user.user_name)
        logger.info(f'[测试模式] 原始任务配置数据已保存：{saved_path}')
    except json.JSONDecodeError:
        logger.warning('无法解析请求体为JSON，跳过测试数据保存')
    except Exception as file_exc:
        logger.warning(f'保存测试数据失败：{file_exc}')

    try:
        # 调用统一处理流程（仅保存，不生成任务）
        result = await TaskService.process_task_config_services(
            query_db=query_db,
            raw_data=raw_body,
            current_user_id=current_user.user.user_id,
            current_user_name=current_user.user.user_name,
            generate_tasks=False,  # 仅保存，不生成
        )

        # 提交事务（如果持久化成功）
        await query_db.commit()

        logger.info(f'任务配置保存成功: {result.message}')
        
        # 返回成功消息和完整数据（如果查询成功）
        if result.result:
            return ResponseUtil.success(msg=result.message, data=result.result)
        else:
            return ResponseUtil.success(msg=result.message)

    except ServiceException as e:
        # 业务异常（校验失败等）
        logger.warning(f'任务配置保存失败: {e.message}')
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message, data=e.data)

    except Exception as e:
        # 其他异常
        logger.error(f'任务配置保存异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'任务配置保存失败：{str(e)}')


@taskController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckWorkbenchMenuAuth())]
)
async def get_task_config_list(
    request: Request,
    task_page_query: TaskConfigPageQueryModel = Depends(TaskConfigPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    查询任务配置列表（测试模式）
    返回空列表，不进行数据库查询
    """
    logger.info('[测试模式] 查询任务配置列表请求（已停用业务逻辑）')
    
    # 返回空列表
    from utils.page_util import PageResponseModel
    empty_result = PageResponseModel(
        rows=[],
        total=0,
        page_num=task_page_query.page_num,
        page_size=task_page_query.page_size,
    )

    return ResponseUtil.success(model_content=empty_result)


@taskController.get(
    '/{task_id}', response_model=TaskConfigModel, dependencies=[Depends(CheckWorkbenchMenuAuth())]
)
async def get_task_config_detail(
    request: Request,
    task_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """
    查询任务配置详情（测试模式）
    返回空数据，不进行数据库查询
    """
    logger.info(f'[测试模式] 查询任务配置详情请求 task_id={task_id}（已停用业务逻辑）')
    
    # 返回空数据
    empty_result = TaskConfigModel()

    return ResponseUtil.success(data=empty_result)


@taskController.get(
    '/project/list', dependencies=[Depends(CheckWorkbenchMenuAuth())]
)
async def get_project_summary_list(query_db: AsyncSession = Depends(get_db)):
    """
    获取项目列表摘要
    """
    data = await TaskService.get_project_summary_list_services(query_db)
    return ResponseUtil.success(data=data)


@taskController.post('/save-and-generate', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def save_and_generate_task_config(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    保存任务配置并生成任务
    统一处理流程：结构校验 -> 内容校验 -> 数据持久化 -> 生成任务
    适用于：
    1. 未生成任务的项目：在任务配置页面直接生成任务
    2. 已生成任务的项目：配置完成后直接生成满足条件的任务
    """
    logger.info(f'收到任务配置保存并生成请求，用户：{current_user.user.user_name}')

    # 读取原始请求体
    raw_body = await request.body()

    # 保存测试数据，便于排查问题
    try:
        parsed_body = json.loads(raw_body.decode('utf-8'))
        saved_path = save_test_data_to_file(parsed_body, current_user.user.user_name)
        logger.info(f'[测试模式] 原始任务配置数据已保存：{saved_path}')
    except json.JSONDecodeError:
        logger.warning('无法解析请求体为JSON，跳过测试数据保存')
    except Exception as file_exc:
        logger.warning(f'保存测试数据失败：{file_exc}')

    try:
        # 调用统一处理流程（保存并生成任务）
        result = await TaskService.process_task_config_services(
            query_db=query_db,
            raw_data=raw_body,
            current_user_id=current_user.user.user_id,
            current_user_name=current_user.user.user_name,
            generate_tasks=True,  # 保存并生成
        )

        # 提交事务（如果持久化成功）
        await query_db.commit()

        logger.info(f'任务配置保存并生成成功: {result.message}')
        
        # 返回成功消息和完整数据（如果查询成功）
        if result.result:
            return ResponseUtil.success(msg=result.message, data=result.result)
        else:
            return ResponseUtil.success(msg=result.message)

    except ServiceException as e:
        # 业务异常（校验失败等）
        logger.warning(f'任务配置保存并生成失败: {e.message}')
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message, data=e.data)

    except Exception as e:
        # 其他异常
        logger.error(f'任务配置保存并生成异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'任务配置保存并生成失败：{str(e)}')


@taskController.get(
    '/project/{project_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())]
)
async def get_project_full_detail(project_id: int, query_db: AsyncSession = Depends(get_db)):
    """
    根据项目ID返回完整的阶段/任务数据
    """
    data = await TaskService.get_task_config_by_project_id_services(query_db, project_id=project_id)
    return ResponseUtil.success(data=data)
