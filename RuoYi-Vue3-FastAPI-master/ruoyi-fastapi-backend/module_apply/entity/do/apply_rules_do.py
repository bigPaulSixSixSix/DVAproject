from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from config.database import Base


class ApplyRules(Base):
    """
    审批规则表
    """

    __tablename__ = 'apply_rules'
    __table_args__ = (
        Index('idx_current_approval_node', 'current_approval_node'),
        {'comment': '审批规则表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    apply_id = Column(String(64), nullable=False, unique=True, comment='申请单ID（关联apply_primary.apply_id）')
    approval_nodes = Column(Text, nullable=True, comment='审批节点数组（JSON格式，存储编制ID列表，oa_department.id）')
    approved_nodes = Column(Text, nullable=True, comment='已审批节点数组（JSON格式，存储已审批的编制ID列表，oa_department.id）')
    current_approval_node = Column(BigInteger, nullable=True, comment='当前审批节点（编制ID，oa_department.id，可为null）')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
