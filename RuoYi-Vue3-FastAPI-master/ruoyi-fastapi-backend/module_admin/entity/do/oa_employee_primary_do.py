from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, DateTime, Integer, Numeric, String
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class OaEmployeePrimary(Base):
    """
    员工主表（真实表）
    """

    __tablename__ = 'oa_employee_primary'
    __table_args__ = {'comment': '员工主表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    name = Column(String(50), nullable=True, server_default="''", comment='姓名')
    job_number = Column(String(20), nullable=True, server_default="''", comment='工号')
    internet_number = Column(String(20), nullable=True, server_default="''", comment='网络编号')
    identity_number = Column(String(18), nullable=True, server_default="''", comment='身份证号')
    company_id = Column(BigInteger, nullable=True, server_default='0', comment='公司ID')
    organization_id = Column(BigInteger, nullable=True, server_default='0', comment='组织ID')
    rank_id = Column(BigInteger, nullable=True, server_default='0', comment='职级ID')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态')
    phone = Column(String(20), nullable=True, server_default="''", comment='手机号')
    job_type = Column(CHAR(1), nullable=True, server_default='0', comment='工作类型')
    special_work_type = Column(CHAR(1), nullable=True, server_default='0', comment='特殊工作类型')
    push_id = Column(String(100), nullable=True, server_default="''", comment='推送ID')
    bma_push_id = Column(String(100), nullable=True, server_default="''", comment='BMA推送ID')
    agree_policy_flag = Column(CHAR(1), nullable=True, server_default='0', comment='同意政策标志')
    avatar_image = Column(String(500), nullable=True, server_default="''", comment='头像图片')
    sex = Column(CHAR(1), nullable=True, server_default='0', comment='性别(1男2女)')
    resign_status = Column(CHAR(1), nullable=True, server_default='0', comment='离职状态')
    entry_date = Column(DateTime, nullable=True, comment='入职日期')
    variable_entry_date = Column(DateTime, nullable=True, comment='可变入职日期')
    correction_date = Column(DateTime, nullable=True, comment='转正日期')
    resign_date = Column(DateTime, nullable=True, comment='离职日期')
    attendance_type = Column(CHAR(1), nullable=True, server_default='0', comment='考勤类型')
    formation_type = Column(CHAR(1), nullable=True, server_default='0', comment='编制类型')
    salary_type = Column(CHAR(1), nullable=True, server_default='0', comment='薪资类型')
    unit_salary = Column(Numeric(10, 2), nullable=True, server_default='0.00', comment='单位薪资')
    birthday = Column(String(10), nullable=True, server_default="''", comment='生日')
    sales_department_id = Column(BigInteger, nullable=True, server_default='0', comment='销售部门ID')
    sales_status = Column(CHAR(1), nullable=True, server_default='0', comment='销售状态')
    sales_rank_id = Column(BigInteger, nullable=True, server_default='0', comment='销售职级ID')
    protocol_expiration_time = Column(DateTime, nullable=True, comment='协议到期时间')
    interviewer_job_number = Column(String(20), nullable=True, server_default="''", comment='面试员工号')
    special_type = Column(CHAR(1), nullable=True, server_default='0', comment='特殊类型')
    reserve_flag = Column(CHAR(1), nullable=True, server_default='0', comment='储备标志')
    protocol_type = Column(CHAR(1), nullable=True, server_default='0', comment='协议类型')
    important_flag = Column(CHAR(1), nullable=True, server_default='0', comment='重要标志')
    study_system_flag = Column(CHAR(1), nullable=True, server_default='0', comment='学习系统标志')
    performance_flag = Column(CHAR(1), nullable=True, server_default='0', comment='绩效标志')
    enable = Column(CHAR(1), nullable=True, server_default='1', comment='启用状态')
    gmt_create_by = Column(String(64), nullable=True, server_default="''", comment='创建人')
    gmt_create_time = Column(DateTime, nullable=True, comment='创建时间')
    gmt_modify_by = Column(String(64), nullable=True, server_default="''", comment='修改人')
    gmt_modify_time = Column(DateTime, nullable=True, comment='修改时间')
