from datetime import datetime
from sqlalchemy import BigInteger, CHAR, Column, DateTime, String
from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class SysUserLocal(Base):
    """
    本地用户表（用于同步真实表数据 + 存储密码等本地字段）
    """

    __tablename__ = 'sys_user_local'
    __table_args__ = {'comment': '本地用户表'}

    user_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='用户ID（本地主键）')
    employee_id = Column(
        BigInteger,
        nullable=False,
        comment='员工ID（关联 oa_employee_primary.id）',
    )
    job_number = Column(String(20), nullable=False, comment='工号（登录账号）')
    password = Column(String(100), nullable=True, server_default="''", comment='密码')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='帐号状态（0正常 1停用）')
    enable = Column(CHAR(1), nullable=True, server_default='1', comment='启用状态（0禁用 1启用）')
    login_ip = Column(String(128), nullable=True, server_default="''", comment='最后登录IP')
    login_date = Column(DateTime, nullable=True, comment='最后登录时间')
    pwd_update_date = Column(DateTime, nullable=True, comment='密码最后更新时间')
    sync_time = Column(DateTime, nullable=True, comment='数据同步时间')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间', default=datetime.now())
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间', default=datetime.now())
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
