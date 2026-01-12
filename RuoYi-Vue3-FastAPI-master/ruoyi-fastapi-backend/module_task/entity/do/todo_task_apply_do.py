from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, String, Text
from config.database import Base


class TodoTaskApply(Base):
    """
    任务申请详情表
    """

    __tablename__ = 'todo_task_apply'
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_submit_time', 'submit_time'),
        {'comment': '任务申请详情表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    apply_id = Column(String(64), nullable=False, unique=True, comment='申请单ID（关联apply_primary.apply_id）')
    task_id = Column(BigInteger, nullable=False, comment='任务ID（关联todo_task.id）')
    submit_text = Column(Text, nullable=True, comment='提交文本')
    submit_images = Column(Text, nullable=True, comment='提交图片（JSON格式，存储图片URL列表）')
    submit_time = Column(DateTime, nullable=True, comment='提交时间')
