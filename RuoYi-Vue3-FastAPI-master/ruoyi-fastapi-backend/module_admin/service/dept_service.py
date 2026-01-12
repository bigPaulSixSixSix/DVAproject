from sqlalchemy.ext.asyncio import AsyncSession
from config.constant import CommonConstant
from exceptions.exception import ServiceException, ServiceWarning
from module_admin.dao.dept_dao import DeptDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.dept_vo import DeptModel
from utils.common_util import CamelCaseUtil
from utils.field_mapper import FieldMapper


class DeptService:
    """
    部门管理模块服务层
    """

    @classmethod
    async def get_dept_tree_services(cls, query_db: AsyncSession, page_object: DeptModel, data_scope_sql: str):
        """
        获取部门树信息service

        :param query_db: orm对象
        :param page_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 部门树信息对象
        """
        dept_list_result = await DeptDao.get_dept_list_for_tree(query_db, page_object, data_scope_sql)
        dept_tree_result = cls.list_to_tree(dept_list_result)

        return dept_tree_result

    @classmethod
    async def get_dept_list_services(cls, query_db: AsyncSession, page_object: DeptModel, data_scope_sql: str):
        """
        获取部门列表信息service

        :param query_db: orm对象
        :param page_object: 分页查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 部门列表信息对象
        """
        dept_list_result = await DeptDao.get_dept_list(query_db, page_object, data_scope_sql)

        # 使用字段映射工具转换数据格式
        mapped_result = [FieldMapper.map_dept_to_sys_format(dept) for dept in dept_list_result]

        return CamelCaseUtil.transform_result(mapped_result)

    @classmethod
    async def check_dept_data_scope_services(cls, query_db: AsyncSession, dept_id: int, data_scope_sql: str):
        """
        校验部门是否有数据权限service

        :param query_db: orm对象
        :param dept_id: 部门id
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 校验结果
        """
        depts = await DeptDao.get_dept_list(query_db, DeptModel(deptId=dept_id), data_scope_sql)
        if depts:
            return CrudResponseModel(is_success=True, message='校验通过')
        else:
            raise ServiceException(message='没有权限访问部门数据')

    @classmethod
    async def dept_detail_services(cls, query_db: AsyncSession, dept_id: int):
        """
        获取部门详细信息service

        :param query_db: orm对象
        :param dept_id: 部门id
        :return: 部门id对应的信息
        """
        dept = await DeptDao.get_dept_detail_by_id(query_db, dept_id=dept_id)
        if dept:
            # 使用字段映射工具转换数据格式
            mapped_dept = FieldMapper.map_dept_to_sys_format(dept)
            result = DeptModel(**CamelCaseUtil.transform_result(mapped_dept))
        else:
            result = DeptModel(**dict())

        return result

    @classmethod
    def list_to_tree(cls, permission_list: list) -> list:
        """
        工具方法：根据部门列表信息生成树形嵌套数据
        支持真实表对象和映射后的字典

        :param permission_list: 部门列表信息（OaDepartment对象或映射后的字典）
        :return: 部门树形嵌套数据
        """
        # 如果是对象，先转换为字典格式
        if permission_list and hasattr(permission_list[0], 'id'):
            # 是真实表对象，使用字段映射工具转换
            permission_list = [FieldMapper.convert_dept_tree_item(item) for item in permission_list]
        elif permission_list and isinstance(permission_list[0], dict):
            # 已经是字典格式，检查是否需要转换
            if 'dept_id' in permission_list[0]:
                # 是映射后的字典，使用字段映射工具转换（统一格式：部门名称-部门ID）
                permission_list = [FieldMapper.convert_dept_tree_item(item) for item in permission_list]
            # 如果已经是树形格式（有id和label），直接使用
        
        # 转成id为key的字典
        mapping: dict = dict(zip([i['id'] for i in permission_list], permission_list))

        # 树容器
        container: list = []

        for d in permission_list:
            # 如果找不到父级项，则是根节点
            parent: dict = mapping.get(d['parentId'])
            if parent is None:
                container.append(d)
            else:
                children: list = parent.get('children')
                if not children:
                    children = []
                children.append(d)
                parent.update({'children': children})

        return container
