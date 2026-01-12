from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, DateTime, Integer, String
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class OaDepartment(Base):
    """
    部门表（真实表）
    """

    __tablename__ = 'oa_department'
    __table_args__ = {'comment': '部门表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    name = Column(String(100), nullable=True, server_default="''", comment='部门名称')
    code = Column(String(50), nullable=True, server_default="''", comment='部门代码')
    parent_id = Column(BigInteger, nullable=True, server_default='0', comment='父部门ID')
    description = Column(String(255), nullable=True, server_default="''", comment='描述')
    sort_no = Column(Integer, nullable=True, server_default='0', comment='排序号')
    area_id = Column(BigInteger, nullable=True, server_default='0', comment='区域ID')
    project_id = Column(BigInteger, nullable=True, server_default='0', comment='项目ID')
    rank_id = Column(BigInteger, nullable=True, server_default='0', comment='职级ID')
    formation_type = Column(CHAR(1), nullable=True, server_default='0', comment='编制类型')
    linked_subject_id = Column(BigInteger, nullable=True, server_default='0', comment='关联科目ID')
    attendance_type = Column(CHAR(1), nullable=True, server_default='0', comment='考勤类型')
    max_shift_count = Column(Integer, nullable=True, server_default='1', comment='最大班次数')
    belong_shop_item_ids = Column(String(500), nullable=True, server_default="''", comment='所属门店项目IDs')
    post_type = Column(CHAR(1), nullable=True, server_default='0', comment='岗位类型')
    position_biz_type = Column(CHAR(1), nullable=True, server_default='0', comment='职位业务类型')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    enable = Column(CHAR(1), nullable=True, server_default='1', comment='启用状态')
    gmt_create_by = Column(String(64), nullable=True, server_default="''", comment='创建人')
    gmt_create_time = Column(DateTime, nullable=True, comment='创建时间')
    gmt_modify_by = Column(String(64), nullable=True, server_default="''", comment='修改人')
    gmt_modify_time = Column(DateTime, nullable=True, comment='修改时间')
