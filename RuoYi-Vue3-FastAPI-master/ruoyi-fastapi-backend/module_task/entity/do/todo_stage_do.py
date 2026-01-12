from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, Text
from config.database import Base


class TodoStage(Base):
    """
    阶段执行表
    """

    __tablename__ = 'todo_stage'
    __table_args__ = (
        Index('idx_project_id', 'project_id'),
        Index('idx_stage_status', 'stage_status'),
        Index('idx_project_status', 'project_id', 'stage_status'),
        {'comment': '阶段执行表'},
    )

    stage_id = Column(BigInteger, primary_key=True, nullable=False, comment='阶段ID（关联proj_stage.stage_id，主键）')
    project_id = Column(BigInteger, nullable=False, comment='项目ID')
    stage_status = Column(Integer, nullable=False, server_default='0', comment='阶段状态（0-未开始，1-进行中，2-已完成）')
    predecessor_stages = Column(Text, nullable=True, comment='前置阶段ID列表（JSON格式）')
    successor_stages = Column(Text, nullable=True, comment='后置阶段ID列表（JSON格式）')
    actual_start_time = Column(DateTime, nullable=True, comment='实际开始时间')
    actual_complete_time = Column(DateTime, nullable=True, comment='实际完成时间')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
