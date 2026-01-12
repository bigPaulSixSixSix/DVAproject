from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, Date, DateTime, Index, Integer, String, Text
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class ProjStage(Base):
    """
    项目阶段表
    """

    __tablename__ = 'proj_stage'
    __table_args__ = (
        Index('idx_proj_stage_project_id', 'project_id'),
        Index('idx_proj_stage_project_enable', 'project_id', 'enable'),
        {'comment': '项目阶段表'},
    )

    stage_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='阶段ID（主键，自增）')
    project_id = Column(BigInteger, nullable=False, comment='所属项目ID')
    name = Column(String(200), nullable=False, comment='阶段名称')
    start_time = Column(Date, nullable=True, comment='开始日期')
    end_time = Column(Date, nullable=True, comment='结束日期')
    duration = Column(Integer, nullable=True, comment='持续天数')
    predecessor_stages = Column(Text, nullable=True, comment='前置阶段ID列表（JSON格式）')
    successor_stages = Column(Text, nullable=True, comment='后置阶段ID列表（JSON格式）')
    position = Column(Text, nullable=True, comment='阶段位置信息（JSON格式，包含x、y、height等）')
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

