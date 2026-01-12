from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from config.database import Base


class ApplyLog(Base):
    """
    审批日志表
    """

    __tablename__ = 'apply_log'
    __table_args__ = (
        Index('idx_apply_id', 'apply_id'),
        Index('idx_approval_node', 'approval_node'),
        Index('idx_approver_id', 'approver_id'),
        Index('idx_approval_result', 'approval_result'),
        {'comment': '审批日志表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    apply_id = Column(String(64), nullable=False, comment='申请单ID（关联apply_primary.apply_id）')
    approval_node = Column(BigInteger, nullable=False, comment='审批节点（编制ID，oa_department.id）')
    approver_id = Column(String(64), nullable=False, comment='审批人工号')
    approval_result = Column(Integer, nullable=False, comment='审批结果（0-申请提交，1-同意，2-驳回）')
    approval_comment = Column(Text, nullable=True, comment='审批意见')
    approval_images = Column(Text, nullable=True, comment='审批意见附图（JSON格式，存储图片URL列表）')
    approval_start_time = Column(DateTime, nullable=True, comment='审批开始时间')
    approval_end_time = Column(DateTime, nullable=True, comment='审批结束时间')
