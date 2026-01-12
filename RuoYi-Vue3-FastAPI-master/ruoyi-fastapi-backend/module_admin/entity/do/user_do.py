from sqlalchemy import BigInteger, Column
from config.database import Base


class SysUserRole(Base):
    """
    用户和角色关联表
    """

    __tablename__ = 'sys_user_role'
    __table_args__ = {'comment': '用户和角色关联表'}

    user_id = Column(BigInteger, primary_key=True, nullable=False, comment='用户ID')
    role_id = Column(BigInteger, primary_key=True, nullable=False, comment='角色ID')
