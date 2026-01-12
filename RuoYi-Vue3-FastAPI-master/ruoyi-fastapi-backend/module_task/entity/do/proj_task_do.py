from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, Index, Integer, String, Text
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class ProjTask(Base):
    """
    项目任务表
    """

    __tablename__ = 'proj_task'
    __table_args__ = (
        Index('idx_proj_task_project_id', 'project_id'),
        Index('idx_proj_task_stage_id', 'stage_id'),
        Index('idx_proj_task_project_enable', 'project_id', 'enable'),
        {'comment': '项目任务表'},
    )

    task_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='任务ID（主键，自增）')
    project_id = Column(BigInteger, nullable=False, comment='所属项目ID')
    stage_id = Column(BigInteger, nullable=True, comment='所属阶段ID（可为空，表示未归属阶段）')
    name = Column(String(200), nullable=False, comment='任务名称')
    description = Column(Text, nullable=True, comment='任务描述')
    start_time = Column(Date, nullable=True, comment='开始日期')
    end_time = Column(Date, nullable=True, comment='结束日期')
    duration = Column(Integer, nullable=True, comment='持续天数')
    job_number = Column(String(64), nullable=True, comment='负责人工号')
    predecessor_tasks = Column(Text, nullable=True, comment='前置任务ID列表（JSON格式）')
    successor_tasks = Column(Text, nullable=True, comment='后置任务ID列表（JSON格式）')
    position = Column(Text, nullable=True, comment='任务位置信息（JSON格式，包含x、y等）')
    approval_type = Column(String(32), nullable=True, comment='审批模式（specified-指定编制审批，sequential-逐级审批）')
    approval_nodes = Column(Text, nullable=True, comment='审批节点数组（JSON格式，存储编制ID列表，oa_department.id）')
    enable = Column(CHAR(1), nullable=False, server_default='1', comment='有效性（1有效 0无效，用于软删除）')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )

