from fastapi import Depends
from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import PermissionException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from config.get_db import get_db


class CheckUserInterfaceAuth:
    """
    校验当前用户是否具有相应的接口权限
    """

    def __init__(self, perm: Union[str, List], is_strict: bool = False):
        """
        校验当前用户是否具有相应的接口权限

        :param perm: 权限标识
        :param is_strict: 当传入的权限标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个权限标识，所有的校验结果都需要为True才会通过
        """
        self.perm = perm
        self.is_strict = is_strict

    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        user_auth_list = current_user.permissions
        # 确保 user_auth_list 是列表类型
        if not isinstance(user_auth_list, list):
            from utils.log_util import logger
            logger.error(f'权限列表类型错误: user_id={current_user.user.user_id if current_user.user else None}, permissions类型={type(user_auth_list)}, permissions={user_auth_list}')
            user_auth_list = list(user_auth_list) if user_auth_list else []
        if '*:*:*' in user_auth_list:
            return True
        if isinstance(self.perm, str):
            if self.perm in user_auth_list:
                return True
        if isinstance(self.perm, list):
            if self.is_strict:
                if all([perm_str in user_auth_list for perm_str in self.perm]):
                    return True
            else:
                if any([perm_str in user_auth_list for perm_str in self.perm]):
                    return True
        raise PermissionException(data='', message='该用户无此接口权限')


class CheckRoleInterfaceAuth:
    """
    根据角色校验当前用户是否具有相应的接口权限
    """

    def __init__(self, role_key: Union[str, List], is_strict: bool = False):
        """
        根据角色校验当前用户是否具有相应的接口权限

        :param role_key: 角色标识
        :param is_strict: 当传入的角色标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个角色标识，所有的校验结果都需要为True才会通过
        """
        self.role_key = role_key
        self.is_strict = is_strict

    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        user_role_list = current_user.user.role
        user_role_key_list = [role.role_key for role in user_role_list]
        if isinstance(self.role_key, str):
            if self.role_key in user_role_key_list:
                return True
        if isinstance(self.role_key, list):
            if self.is_strict:
                if all([role_key_str in user_role_key_list for role_key_str in self.role_key]):
                    return True
            else:
                if any([role_key_str in user_role_key_list for role_key_str in self.role_key]):
                    return True
        raise PermissionException(data='', message='该用户无此接口权限')


class CheckWorkbenchMenuAuth:
    """
    校验当前用户是否具有工作台菜单权限
    用于工作台下的所有功能：如果用户能看到工作台菜单，就能使用其下的所有功能
    """

    async def __call__(
        self, 
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
        query_db: AsyncSession = Depends(get_db)
    ):
        from module_admin.dao.user_dao import UserDao
        from utils.log_util import logger
        
        user_auth_list = current_user.permissions
        # 确保 user_auth_list 是列表类型
        if not isinstance(user_auth_list, list):
            logger.error(f'权限列表类型错误: user_id={current_user.user.user_id if current_user.user else None}, permissions类型={type(user_auth_list)}, permissions={user_auth_list}')
            user_auth_list = list(user_auth_list) if user_auth_list else []
        
        # 超级管理员直接通过
        if '*:*:*' in user_auth_list:
            return True
        
        # 检查用户是否有任何以 task: 开头的菜单权限（工作台相关功能）
        for perm in user_auth_list:
            if perm and perm.startswith('task:'):
                return True
        
        # 如果权限列表中没有 task: 开头的权限，查询用户菜单信息，检查是否有工作台相关菜单
        user_id = current_user.user.user_id if current_user.user else None
        if not user_id:
            logger.warning(f'工作台权限检查失败: 用户ID为空')
            raise PermissionException(data='', message='该用户无此接口权限')
        
        # 查询用户菜单信息，检查是否有工作台相关菜单
        try:
            query_user = await UserDao.get_user_by_id(query_db, user_id=user_id)
            user_menu_info = query_user.get('user_menu_info', []) or []
            
            # 检查用户菜单中是否有工作台相关菜单（菜单名称包含"工作台"或路径包含"workbench"）
            for menu in user_menu_info:
                menu_name = menu.menu_name if hasattr(menu, 'menu_name') else ''
                menu_path = menu.path if hasattr(menu, 'path') else ''
                menu_perms = menu.perms if hasattr(menu, 'perms') else ''
                
                # 检查菜单名称、路径或权限标识是否与工作台相关
                if ('工作台' in menu_name or 
                    'workbench' in (menu_path or '').lower() or 
                    (menu_perms and menu_perms.startswith('task:'))):
                    return True
        except Exception as e:
            logger.error(f'工作台权限检查异常: user_id={user_id}, 错误={str(e)}', exc_info=True)
        
        raise PermissionException(data='', message='该用户无此接口权限')
