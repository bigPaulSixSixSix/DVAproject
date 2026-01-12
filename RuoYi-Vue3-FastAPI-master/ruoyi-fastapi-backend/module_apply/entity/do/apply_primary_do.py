from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String
from config.database import Base


class ApplyPrimary(Base):
    """
    申请主表
    """

    __tablename__ = 'apply_primary'
    __table_args__ = (
        Index('idx_apply_type_status', 'apply_type', 'apply_status'),
        Index('idx_apply_status', 'apply_status'),
        {'comment': '申请主表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    apply_type = Column(Integer, nullable=False, comment='申请类型（1-项目推进任务）')
    apply_id = Column(String(64), nullable=False, unique=True, comment='申请单ID（雪花算法生成，全局唯一）')
    apply_status = Column(Integer, nullable=False, server_default='0', comment='申请单状态（0-审批中，1-完成，2-驳回，3-撤销）')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
