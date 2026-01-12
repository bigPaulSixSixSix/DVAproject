from datetime import datetime
from sqlalchemy import BigInteger, Column, Date, DateTime, Index, Integer, String, Text
from config.database import Base


class TodoTask(Base):
    """
    任务执行表
    """

    __tablename__ = 'todo_task'
    __table_args__ = (
        Index('idx_project_id', 'project_id'),
        Index('idx_stage_id', 'stage_id'),
        Index('idx_job_number', 'job_number'),
        Index('idx_task_status', 'task_status'),
        Index('idx_project_status', 'project_id', 'task_status'),
        {'comment': '任务执行表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    task_id = Column(BigInteger, nullable=False, unique=True, comment='任务ID（关联proj_task.task_id）')
    project_id = Column(BigInteger, nullable=False, comment='项目ID')
    stage_id = Column(BigInteger, nullable=True, comment='阶段ID')
    name = Column(String(200), nullable=False, comment='任务名称')
    description = Column(Text, nullable=True, comment='任务描述')
    start_time = Column(Date, nullable=True, comment='开始日期')
    end_time = Column(Date, nullable=True, comment='结束日期')
    duration = Column(Integer, nullable=True, comment='持续天数')
    job_number = Column(String(64), nullable=True, comment='负责人工号')
    predecessor_tasks = Column(Text, nullable=True, comment='前置任务ID列表（JSON格式）')
    successor_tasks = Column(Text, nullable=True, comment='后置任务ID列表（JSON格式）')
    approval_nodes = Column(Text, nullable=True, comment='审批节点数组（JSON格式，存储编制ID列表，oa_department.id）')
    task_status = Column(Integer, nullable=False, server_default='0', comment='任务状态（0-未开始，1-进行中，2-已提交，3-完成，4-驳回）')
    is_skipped = Column(Integer, nullable=False, server_default='0', comment='是否跳过（0-未跳过，1-已跳过）')
    actual_start_time = Column(DateTime, nullable=True, comment='实际开始时间')
    actual_complete_time = Column(DateTime, nullable=True, comment='实际完成时间')
