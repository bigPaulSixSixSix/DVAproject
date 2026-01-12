from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from typing import Any, Dict, List, Optional, Union
from module_admin.annotation.pydantic_annotation import as_query


# ===== 顶层任务配置模型（用于结构校验） =====
class StagePositionModel(BaseModel):
    """阶段位置模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    x: Optional[int] = Field(default=None, description='横坐标')
    y: Optional[int] = Field(default=None, description='纵坐标')
    width: Optional[int] = Field(default=None, description='宽度')
    height: Optional[int] = Field(default=None, description='高度')


class StageModel(BaseModel):
    """阶段模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    id: int = Field(description='阶段ID')
    name: str = Field(description='阶段名称')
    start_time: Optional[date] = Field(default=None, description='开始日期')
    end_time: Optional[date] = Field(default=None, description='结束日期')
    duration: Optional[int] = Field(default=None, description='持续天数')
    predecessor_stages: List[int] = Field(default_factory=list, description='前置阶段ID列表')
    successor_stages: List[int] = Field(default_factory=list, description='后置阶段ID列表')
    position: Optional[StagePositionModel] = Field(default=None, description='阶段位置')
    project_id: Union[int, str] = Field(description='所属项目ID')

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def _coerce_stage_dates(cls, value):
        return cls._coerce_date_value(value)

    @staticmethod
    def _coerce_date_value(value):
        if value is None or value == '':
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError as exc:
                raise ValueError('日期必须为YYYY-MM-DD格式') from exc
        raise ValueError('日期必须为YYYY-MM-DD格式')


class TaskPositionModel(BaseModel):
    """任务位置模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    x: Optional[int] = Field(default=None, description='横坐标')
    y: Optional[int] = Field(default=None, description='纵坐标')


class TaskModel(BaseModel):
    """任务模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    id: int = Field(description='任务ID')
    name: str = Field(description='任务名称')
    description: Optional[str] = Field(default=None, description='任务描述')
    start_time: Optional[date] = Field(default=None, description='开始日期')
    end_time: Optional[date] = Field(default=None, description='结束日期')
    duration: Optional[int] = Field(default=None, description='持续天数')
    job_number: Optional[str] = Field(default=None, description='负责人工号')
    stage_id: Optional[int] = Field(default=None, description='所属阶段ID')
    predecessor_tasks: List[int] = Field(default_factory=list, description='前置任务ID列表')
    successor_tasks: List[int] = Field(default_factory=list, description='后置任务ID列表')
    position: Optional[TaskPositionModel] = Field(default=None, description='任务位置')
    project_id: Union[int, str] = Field(description='所属项目ID')
    approval_type: Optional[str] = Field(default=None, description='审批模式（specified-指定编制审批，sequential-逐级审批）')
    approval_nodes: List[int] = Field(default_factory=list, description='审批节点数组（岗位ID列表）')

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def _coerce_task_dates(cls, value):
        return StageModel._coerce_date_value(value)


class MetadataModel(BaseModel):
    """元数据模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    user: str = Field(description='请求发起用户名称')
    user_id: Union[int, str] = Field(description='请求发起用户ID')
    received_at: Optional[str] = Field(default=None, description='接收时间')


class TaskConfigPayload(BaseModel):
    """
    任务配置顶层模型（严格校验前端结构）
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    project_id: Union[int, str] = Field(description='项目ID')
    stages: List[StageModel] = Field(default_factory=list, description='阶段列表')
    tasks: List[TaskModel] = Field(default_factory=list, description='任务列表')
    metadata: Optional[MetadataModel] = Field(default=None, alias='_metadata', description='元数据（可选）')


class ProjectSummaryModel(BaseModel):
    """项目列表摘要模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    project_id: int = Field(description='项目ID')
    project_name: str = Field(description='项目名称')
    stage_count: int = Field(default=0, description='阶段数量')
    task_count: int = Field(default=0, description='任务数量')
    create_time: Optional[datetime] = Field(default=None, description='首次创建时间')
    update_time: Optional[datetime] = Field(default=None, description='最近更新时间')
    project_status: str = Field(default='正常', description='项目状态（正常/异常/未配置）')
    missing_info_count: int = Field(default=0, description='信息缺失数（任务：负责人、开始时间、结束时间、审批层级中有任何一项未填写）')
    time_relation_error_count: int = Field(default=0, description='时间关系异常数（阶段+任务：前置结束时间晚于后置开始时间，或自身开始时间晚于结束时间）')
    unassigned_stage_count: int = Field(default=0, description='未分配到阶段数（任务在阶段外）')
    tasks_generated: bool = Field(default=False, description='任务是否已生成（true-已生成，false-未生成）')


# ===== 任务执行相关VO模型 =====
class SubmitTaskModel(BaseModel):
    """提交任务请求模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    submitText: Optional[str] = Field(default=None, description='提交文本')
    submitImages: Optional[List[str]] = Field(default_factory=list, description='提交图片URL列表')


class ApproveTaskModel(BaseModel):
    """审批同意请求模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    approvalComment: Optional[str] = Field(default=None, description='审批意见')
    approvalImages: Optional[List[str]] = Field(default_factory=list, description='审批意见附图URL列表')


class RejectTaskModel(BaseModel):
    """审批驳回请求模型"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    approvalComment: str = Field(description='审批意见（必填）')
    approvalImages: Optional[List[str]] = Field(default_factory=list, description='审批意见附图URL列表')


# ===== 以下模型用于分页/查询接口（保留原有定义） =====
class TaskConfigModel(BaseModel):
    """
    任务配置表对应pydantic模型
    （用于接口返回值，非结构校验）
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    task_id: Optional[int] = Field(default=None, description='任务ID')
    task_name: Optional[str] = Field(default=None, description='任务名称')
    task_data: Optional[Dict[str, Any]] = Field(default=None, description='任务配置数据（JSON格式）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


class TaskConfigQueryModel(BaseModel):
    """
    任务配置管理不分页查询模型
    （查询条件仅包含简单字段）
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    task_id: Optional[int] = Field(default=None, description='任务ID')
    task_name: Optional[str] = Field(default=None, description='任务名称')
    create_by: Optional[str] = Field(default=None, description='创建者')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class TaskConfigPageQueryModel(TaskConfigQueryModel):
    """
    任务配置管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTaskConfigModel(BaseModel):
    """
    删除任务配置模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    task_ids: str = Field(description='需要删除的任务ID')


class WorkbenchTaskStatsModel(BaseModel):
    """
    工作台任务统计模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

    pendingSubmit: int = Field(default=0, description='待提交任务数量')
    pendingApprove: int = Field(default=0, description='待审批任务数量')
    rejected: int = Field(default=0, description='被驳回任务数量')

