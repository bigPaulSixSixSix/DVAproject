"""
岗位管理Controller（只读，数据来自真实表 oa_rank）
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.do.oa_rank_do import OaRank
from module_admin.entity.vo.post_vo import PostPageQueryModel
from module_admin.service.login_service import LoginService
from utils.log_util import logger
from utils.page_util import PageResponseModel, PageUtil
from utils.response_util import ResponseUtil


postController = APIRouter(prefix='/system/post', dependencies=[Depends(LoginService.get_current_user)])


@postController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:post:list'))]
)
async def get_system_post_list(
    request: Request,
    post_page_query: PostPageQueryModel = Depends(PostPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取岗位列表（只读，数据来自真实表 oa_rank）
    岗位信息来自真实表 oa_rank，只读
    """
    # 从 oa_rank 获取职级列表（作为岗位列表显示，只读）
    # 使用 SQL 别名直接映射字段名，避免后续转换
    conditions = [OaRank.enable == '1']
    
    # 支持按岗位名称和编码查询
    if post_page_query.post_name:
        conditions.append(OaRank.rank_name.like(f'%{post_page_query.post_name}%'))
    if post_page_query.post_code:
        conditions.append(OaRank.rank_code.like(f'%{post_page_query.post_code}%'))
    
    # 使用别名直接映射字段名：oa_rank 字段 → sys_post 字段
    query = (
        select(
            OaRank.id.label('post_id'),
            OaRank.rank_code.label('post_code'),
            OaRank.rank_name.label('post_name'),
            OaRank.order_no.label('post_sort'),
            OaRank.enable.label('status'),  # enable='1' → status='0'（正常），需要在查询后转换
            OaRank.gmt_create_by.label('create_by'),
            OaRank.gmt_create_time.label('create_time'),
            OaRank.gmt_modify_by.label('update_by'),
            OaRank.gmt_modify_time.label('update_time'),
            OaRank.rank_description.label('remark'),
        )
        .where(*conditions)
        .order_by(OaRank.order_no)
    )
    
    # 分页查询
    post_list_result = await PageUtil.paginate(
        query_db, query, post_page_query.page_num, post_page_query.page_size, is_page=True
    )
    
    # 转换 status：enable='1' → status='0'（正常），enable='0' → status='1'（停用）
    # 注意：由于使用了 label('status')，row['status'] 的值实际上是 enable 的值
    if isinstance(post_list_result, PageResponseModel):
        for row in post_list_result.rows:
            if isinstance(row, dict):
                # status 字段：enable='1' → '0'（正常），enable='0' → '1'（停用）
                # 由于使用了 label('status')，row['status'] 的值实际上是 enable 的值
                enable_value = row.get('status')  # 这里实际上是 enable 的值
                # enable='1'（启用）→ status='0'（正常），enable='0'（停用）→ status='1'（停用）
                row['status'] = '0' if str(enable_value) == '1' else '1'
    
    return ResponseUtil.success(model_content=post_list_result)
