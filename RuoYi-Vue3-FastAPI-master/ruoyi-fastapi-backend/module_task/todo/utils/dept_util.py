"""
部门工具类
"""
from typing import Optional


class DeptUtil:
    """部门工具类"""
    
    @staticmethod
    def get_second_level_dept_code(dept_code: Optional[str]) -> Optional[str]:
        """
        获取第二级部门code（取前5位）
        
        code编码规则：
        - 头两位数字（02）代表一级部门
        - 第3-5位（1个字母A + 2位数字）代表二级部门
        - 例如：02A01B01C01 → 二级部门是 02A01
        
        :param dept_code: 部门code
        :return: 第二级部门code（前5位），如果code为空或长度不足，返回原值
        """
        if not dept_code:
            return None
        
        # 如果code长度不足5位，返回原值
        if len(dept_code) < 5:
            return dept_code
        
        # 取前5位作为第二级部门code
        return dept_code[:5]
