from fastapi import Request
from config.enums import RedisInitKeyConfig
from config.get_redis import RedisUtil
from module_admin.entity.vo.cache_vo import CacheInfoModel, CacheMonitorModel
from module_admin.entity.vo.common_vo import CrudResponseModel
from exceptions.exception import ServiceException


class CacheService:
    """
    缓存监控模块服务层
    """

    @classmethod
    def _get_project_key_prefixes(cls):
        """
        获取本项目使用的所有Redis key前缀列表
        用于限制缓存操作范围，避免影响其他项目的数据

        :return: key前缀列表
        """
        return [key_config.key for key_config in RedisInitKeyConfig]

    @classmethod
    def _validate_cache_name(cls, cache_name: str):
        """
        验证缓存名称是否为本项目定义的缓存类型

        :param cache_name: 缓存名称
        :raises ServiceException: 如果缓存名称不在允许列表中
        """
        valid_names = cls._get_project_key_prefixes()
        if cache_name not in valid_names:
            raise ServiceException(message=f'无效的缓存名称: {cache_name}，只允许操作本项目定义的缓存类型')

    @classmethod
    async def get_cache_monitor_statistical_info_services(cls, request: Request):
        """
        获取缓存监控信息service

        :param request: Request对象
        :return: 缓存监控信息
        """
        info = await request.app.state.redis.info()
        db_size = await request.app.state.redis.dbsize()
        command_stats_dict = await request.app.state.redis.info('commandstats')
        command_stats = [
            dict(name=key.split('_')[1], value=str(value.get('calls'))) for key, value in command_stats_dict.items()
        ]
        result = CacheMonitorModel(commandStats=command_stats, dbSize=db_size, info=info)

        return result

    @classmethod
    async def get_cache_monitor_cache_name_services(cls):
        """
        获取缓存名称列表信息service

        :return: 缓存名称列表信息
        """
        name_list = []
        for key_config in RedisInitKeyConfig:
            name_list.append(
                CacheInfoModel(
                    cacheKey='',
                    cacheName=key_config.key,
                    cacheValue='',
                    remark=key_config.remark,
                )
            )

        return name_list

    @classmethod
    async def get_cache_monitor_cache_key_services(cls, request: Request, cache_name: str):
        """
        获取缓存键名列表信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 缓存键名列表信息
        """
        cache_keys = await request.app.state.redis.keys(f'{cache_name}*')
        cache_key_list = [key.split(':', 1)[1] for key in cache_keys if key.startswith(f'{cache_name}:')]

        return cache_key_list

    @classmethod
    async def get_cache_monitor_cache_value_services(cls, request: Request, cache_name: str, cache_key: str):
        """
        获取缓存内容信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :param cache_key: 缓存键名
        :return: 缓存内容信息
        """
        cache_value = await request.app.state.redis.get(f'{cache_name}:{cache_key}')

        return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=cache_value, remark='')

    @classmethod
    async def clear_cache_monitor_cache_name_services(cls, request: Request, cache_name: str):
        """
        清除缓存名称对应所有键值service
        限制为只清除本项目定义的缓存类型，避免影响其他项目的数据

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 操作缓存响应信息
        """
        # 验证缓存名称是否为本项目定义的缓存类型
        cls._validate_cache_name(cache_name)
        
        # 只清除以指定前缀开头的key，确保只操作本项目的缓存
        cache_keys = await request.app.state.redis.keys(f'{cache_name}:*')
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        return CrudResponseModel(is_success=True, message=f'{cache_name}对应键值清除成功')

    @classmethod
    async def clear_cache_monitor_cache_key_services(cls, request: Request, cache_key: str):
        """
        清除缓存键名对应的所有键值service
        限制为只清除本项目定义的缓存类型，避免影响其他项目的数据

        :param request: Request对象
        :param cache_key: 缓存键名（不包含前缀）
        :return: 操作缓存响应信息
        """
        # 获取本项目使用的所有key前缀
        key_prefixes = cls._get_project_key_prefixes()
        
        # 只在本项目定义的key前缀下查找匹配的key
        all_matched_keys = []
        for prefix in key_prefixes:
            pattern = f'{prefix}:*{cache_key}*'
            matched_keys = await request.app.state.redis.keys(pattern)
            all_matched_keys.extend(matched_keys)
        
        # 去重
        unique_keys = list(set(all_matched_keys))
        if unique_keys:
            await request.app.state.redis.delete(*unique_keys)

        return CrudResponseModel(is_success=True, message=f'{cache_key}清除成功')

    @classmethod
    async def clear_cache_monitor_all_services(cls, request: Request):
        """
        清除本项目相关的所有缓存service
        限制为只清除本项目定义的缓存类型，避免影响其他项目的数据

        :param request: Request对象
        :return: 操作缓存响应信息
        """
        # 获取本项目使用的所有key前缀
        key_prefixes = cls._get_project_key_prefixes()
        
        # 只清除本项目定义的key前缀下的所有key
        all_keys = []
        for prefix in key_prefixes:
            pattern = f'{prefix}:*'
            matched_keys = await request.app.state.redis.keys(pattern)
            all_keys.extend(matched_keys)
        
        # 去重并删除
        unique_keys = list(set(all_keys))
        if unique_keys:
            await request.app.state.redis.delete(*unique_keys)

        # 重新初始化系统字典和配置缓存
        await RedisUtil.init_sys_dict(request.app.state.redis)
        await RedisUtil.init_sys_config(request.app.state.redis)

        return CrudResponseModel(is_success=True, message='本项目所有缓存清除成功')
