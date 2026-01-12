"""
字段映射工具类
用于将真实表的字段映射到系统框架期望的字段格式
确保接口返回的数据结构与前端期望一致
"""
from typing import Dict, Any, Optional
from datetime import datetime


class FieldMapper:
    """
    字段映射工具类
    """

    @staticmethod
    def map_dept_to_sys_format(oa_dept: Any) -> Dict[str, Any]:
        """
        将 oa_department 映射到 sys_dept 格式
        
        :param oa_dept: OaDepartment 对象或字典
        :return: 映射后的字典，字段名与 sys_dept 一致
        """
        if oa_dept is None:
            return {}
        
        # 如果是对象，转换为字典
        if hasattr(oa_dept, '__dict__'):
            dept_dict = {k: v for k, v in oa_dept.__dict__.items() if not k.startswith('_')}
        else:
            dept_dict = oa_dept if isinstance(oa_dept, dict) else {}
        
        # 字段映射
        dept_id = dept_dict.get('id')
        dept_name = dept_dict.get('name', '')
        # 部门名称格式：部门名称-deptID（例如：土建管理-87）
        dept_name_with_id = f"{dept_name}-{dept_id}" if dept_name and dept_id is not None else dept_name
        
        mapped = {
            'dept_id': dept_id,
            'dept_name': dept_name_with_id,  # 格式：部门名称-deptID
            'parent_id': dept_dict.get('parent_id', 0),
            'ancestors': '',  # 真实表没有 ancestors，使用空字符串
            'order_num': dept_dict.get('sort_no', 0),
            'leader': '',  # 真实表没有 leader 字段
            'phone': '',  # 真实表没有 phone 字段
            'email': '',  # 真实表没有 email 字段
            'status': FieldMapper._convert_status_to_char(dept_dict.get('status')),
            'del_flag': FieldMapper._convert_enable_to_del_flag(dept_dict.get('enable')),
            'create_by': dept_dict.get('gmt_create_by', ''),
            'create_time': dept_dict.get('gmt_create_time'),
            'update_by': dept_dict.get('gmt_modify_by', ''),
            'update_time': dept_dict.get('gmt_modify_time'),
        }
        
        return mapped

    @staticmethod
    def map_employee_to_user_format(employee: Any, user_local: Any = None) -> Dict[str, Any]:
        """
        将 oa_employee_primary + sys_user_local 映射到 sys_user 格式
        
        :param employee: OaEmployeePrimary 对象或字典
        :param user_local: SysUserLocal 对象或字典（可选）
        :return: 映射后的字典，字段名与 sys_user 一致
        """
        if employee is None:
            return {}
        
        # 如果是对象，转换为字典
        if hasattr(employee, '__dict__'):
            emp_dict = {k: v for k, v in employee.__dict__.items() if not k.startswith('_')}
        else:
            emp_dict = employee if isinstance(employee, dict) else {}
        
        # 处理 user_local
        user_local_dict = {}
        if user_local:
            if hasattr(user_local, '__dict__'):
                user_local_dict = {k: v for k, v in user_local.__dict__.items() if not k.startswith('_')}
            else:
                user_local_dict = user_local if isinstance(user_local, dict) else {}
        
        # 字段映射
        mapped = {
            'user_id': user_local_dict.get('user_id'),  # 使用本地用户表的 user_id
            'dept_id': emp_dict.get('organization_id'),  # organization_id 对应部门ID
            'user_name': user_local_dict.get('job_number') or emp_dict.get('job_number', ''),  # 工号作为登录账号
            'nick_name': emp_dict.get('name', ''),  # 姓名作为昵称
            'user_type': '00',  # 固定为系统用户
            'email': '',  # 真实表没有 email 字段
            'phonenumber': emp_dict.get('phone', ''),
            'sex': FieldMapper._convert_sex_format(emp_dict.get('sex')),  # 1男2女 -> 0男1女2未知
            'avatar': emp_dict.get('avatar_image', ''),
            'password': user_local_dict.get('password', ''),  # 从本地表获取
            'status': FieldMapper._convert_status_to_char(user_local_dict.get('status') or user_local_dict.get('enable')),  # 账号状态
            'del_flag': FieldMapper._convert_enable_to_del_flag(user_local_dict.get('enable')),  # 删除标志
            'login_ip': user_local_dict.get('login_ip', ''),
            'login_date': user_local_dict.get('login_date'),
            'pwd_update_date': user_local_dict.get('pwd_update_date'),
            'create_by': user_local_dict.get('create_by') or emp_dict.get('gmt_create_by', ''),
            'create_time': user_local_dict.get('create_time') or emp_dict.get('gmt_create_time'),
            'update_by': user_local_dict.get('update_by') or emp_dict.get('gmt_modify_by', ''),
            'update_time': user_local_dict.get('update_time') or emp_dict.get('gmt_modify_time'),
            'remark': user_local_dict.get('remark', ''),
        }
        
        return mapped

    @staticmethod
    def map_rank_to_post_format(rank: Any) -> Dict[str, Any]:
        """
        将 oa_rank 映射到 sys_post 格式（用于只读显示）
        
        :param rank: OaRank 对象或字典
        :return: 映射后的字典，字段名与 sys_post 一致
        """
        if rank is None:
            return {}
        
        # 如果是对象，转换为字典
        if hasattr(rank, '__dict__'):
            rank_dict = {k: v for k, v in rank.__dict__.items() if not k.startswith('_')}
        else:
            rank_dict = rank if isinstance(rank, dict) else {}
        
        # 字段映射
        mapped = {
            'post_id': rank_dict.get('id'),
            'post_code': rank_dict.get('rank_code', ''),
            'post_name': rank_dict.get('rank_name', ''),
            'post_sort': rank_dict.get('order_no', 0),
            'status': FieldMapper._convert_status_to_char(rank_dict.get('enable')),  # 使用 enable 字段
            'create_by': rank_dict.get('gmt_create_by', ''),
            'create_time': rank_dict.get('gmt_create_time'),
            'update_by': rank_dict.get('gmt_modify_by', ''),
            'update_time': rank_dict.get('gmt_modify_time'),
            'remark': rank_dict.get('rank_description', ''),
        }
        
        return mapped

    @staticmethod
    def _convert_status_to_char(status: Any) -> str:
        """
        将状态值转换为字符格式（'0' 或 '1'）
        
        :param status: 状态值（可能是 int, str, None）
        :return: '0' 或 '1'
        """
        if status is None:
            return '0'
        
        # 如果是字符串，直接返回
        if isinstance(status, str):
            return status if status in ['0', '1'] else '0'
        
        # 如果是数字，转换为字符串
        if isinstance(status, (int, bool)):
            return '1' if status else '0'
        
        return '0'

    @staticmethod
    def _convert_enable_to_del_flag(enable: Any) -> str:
        """
        将 enable 字段转换为 del_flag 格式
        enable: 1启用 -> del_flag: '0'存在
        enable: 0禁用 -> del_flag: '2'删除
        
        :param enable: enable 值（可能是 int, str, None）
        :return: '0' 或 '2'
        """
        if enable is None:
            return '0'
        
        # 如果是字符串
        if isinstance(enable, str):
            # enable='1' 表示启用，对应 del_flag='0'（存在）
            # enable='0' 表示禁用，对应 del_flag='2'（删除）
            return '0' if enable == '1' else '2'
        
        # 如果是数字
        if isinstance(enable, (int, bool)):
            # enable=1 表示启用，对应 del_flag='0'（存在）
            # enable=0 表示禁用，对应 del_flag='2'（删除）
            return '0' if enable else '2'
        
        return '0'

    @staticmethod
    def _convert_sex_format(sex: Any) -> str:
        """
        将性别格式转换
        真实表：1男 2女
        系统表：0男 1女 2未知
        
        :param sex: 性别值（可能是 int, str, None）
        :return: '0', '1', 或 '2'
        """
        if sex is None:
            return '2'  # 未知
        
        # 如果是字符串
        if isinstance(sex, str):
            if sex == '1':
                return '0'  # 男
            elif sex == '2':
                return '1'  # 女
            else:
                return '2'  # 未知
        
        # 如果是数字
        if isinstance(sex, int):
            if sex == 1:
                return '0'  # 男
            elif sex == 2:
                return '1'  # 女
            else:
                return '2'  # 未知
        
        return '2'  # 未知

    @staticmethod
    def convert_dept_tree_item(dept: Any) -> Dict[str, Any]:
        """
        将部门对象转换为树形结构需要的格式
        用于 list_to_tree 方法
        label 格式：部门名称-部门ID（例如：安装管理-129）
        
        :param dept: 部门对象（已映射的字典或原始对象）
        :return: {id, label, parentId} 格式的字典
        """
        if dept is None:
            return {}
        
        # 如果已经是映射后的字典
        if isinstance(dept, dict):
            dept_id = dept.get('dept_id')
            dept_name = dept.get('dept_name', '')
            # dept_name 已经是"部门名称-deptID"格式，直接使用
            label = dept_name if dept_name else (str(dept_id) if dept_id is not None else '')
            return {
                'id': dept_id,
                'label': label,
                'parentId': dept.get('parent_id', 0),
            }
        
        # 如果是原始对象，先映射
        mapped = FieldMapper.map_dept_to_sys_format(dept)
        dept_id = mapped.get('dept_id')
        dept_name = mapped.get('dept_name', '')
        # dept_name 已经是"部门名称-deptID"格式，直接使用
        label = dept_name if dept_name else (str(dept_id) if dept_id is not None else '')
        return {
            'id': dept_id,
            'label': label,
            'parentId': mapped.get('parent_id', 0),
        }
