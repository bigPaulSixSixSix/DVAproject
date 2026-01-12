from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, DateTime, Integer, Numeric, String
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class OaRank(Base):
    """
    职级表（真实表）
    """

    __tablename__ = 'oa_rank'
    __table_args__ = {'comment': '职级表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    rank_name = Column(String(50), nullable=True, server_default="''", comment='职级名称')
    rank_code = Column(String(50), nullable=True, server_default="''", comment='职级代码')
    rank_description = Column(String(255), nullable=True, server_default="''", comment='职级描述')
    node_penalty = Column(Integer, nullable=True, server_default='0', comment='节点处罚')
    order_no = Column(Integer, nullable=True, server_default='0', comment='排序号')
    rank_level = Column(String(10), nullable=True, server_default="''", comment='职级等级')
    real_flag = Column(CHAR(1), nullable=True, server_default='1', comment='真实标志')
    hotel_standard = Column(Numeric(10, 2), nullable=True, server_default='0.00', comment='酒店标准')
    meal_standard = Column(Numeric(10, 2), nullable=True, server_default='0.00', comment='餐费标准')
    salary_from = Column(Numeric(10, 2), nullable=True, server_default='0.00', comment='薪资范围-起始')
    salary_to = Column(Numeric(10, 2), nullable=True, server_default='0.00', comment='薪资范围-结束')
    enable = Column(CHAR(1), nullable=True, server_default='1', comment='启用状态')
    gmt_create_by = Column(String(64), nullable=True, server_default="''", comment='创建人')
    gmt_create_time = Column(DateTime, nullable=True, comment='创建时间')
    gmt_modify_by = Column(String(64), nullable=True, server_default="''", comment='修改人')
    gmt_modify_time = Column(DateTime, nullable=True, comment='修改时间')
