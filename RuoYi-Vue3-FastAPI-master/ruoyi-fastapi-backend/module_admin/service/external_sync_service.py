"""
外部数据库同步服务
用于从外部数据库同步基础信息表到本系统数据库
"""
from datetime import datetime
from sqlalchemy import create_engine, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
from config.env import SourceDataBaseConfig, DataBaseConfig
from config.database import AsyncSessionLocal
from module_admin.entity.do.oa_department_do import OaDepartment
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.oa_rank_do import OaRank
from utils.log_util import logger
from urllib.parse import quote_plus


class ExternalSyncService:
    """
    外部数据库同步服务
    """

    @classmethod
    def _get_source_db_url(cls) -> str:
        """
        获取源数据库连接URL
        
        :return: 数据库连接URL
        """
        if SourceDataBaseConfig.source_db_type == "postgresql":
            return (
                f'postgresql+psycopg2://{SourceDataBaseConfig.source_db_username}:'
                f'{quote_plus(SourceDataBaseConfig.source_db_password)}@'
                f'{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/'
                f'{SourceDataBaseConfig.source_db_database}'
            )
        else:
            return (
                f'mysql+pymysql://{SourceDataBaseConfig.source_db_username}:'
                f'{quote_plus(SourceDataBaseConfig.source_db_password)}@'
                f'{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/'
                f'{SourceDataBaseConfig.source_db_database}'
            )

    @classmethod
    def _get_target_db_url(cls) -> str:
        """
        获取目标数据库连接URL
        
        :return: 数据库连接URL
        """
        if DataBaseConfig.db_type == "postgresql":
            return (
                f'postgresql+psycopg2://{DataBaseConfig.db_username}:'
                f'{quote_plus(DataBaseConfig.db_password)}@'
                f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/'
                f'{DataBaseConfig.db_database}'
            )
        else:
            return (
                f'mysql+pymysql://{DataBaseConfig.db_username}:'
                f'{quote_plus(DataBaseConfig.db_password)}@'
                f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/'
                f'{DataBaseConfig.db_database}'
            )

    @classmethod
    async def sync_oa_rank(cls) -> bool:
        """
        同步 oa_rank 表（全量更新）
        
        :return: 是否成功
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            
            # 检查源数据库配置
            if not SourceDataBaseConfig.source_db_host or SourceDataBaseConfig.source_db_host == "placeholder_host":
                logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库配置未设置）")
                return False
            
            # 连接源数据库
            source_engine = create_engine(cls._get_source_db_url(), pool_pre_ping=True)
            source_session = sessionmaker(bind=source_engine)()
            
            try:
                # 从源数据库查询所有数据
                query = text("SELECT * FROM oa_rank")
                source_data = source_session.execute(query).fetchall()
                
                if not source_data:
                    logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（oa_rank 表无数据）")
                    return False
                
                # 连接目标数据库
                target_engine = create_engine(cls._get_target_db_url(), pool_pre_ping=True)
                target_session = sessionmaker(bind=target_engine)()
                
                try:
                    # 全量更新：先删除所有数据，再插入新数据
                    target_session.execute(delete(OaRank))
                    
                    # 插入新数据
                    for row in source_data:
                        row_dict = dict(row._mapping)
                        target_session.execute(
                            text("""
                                INSERT INTO oa_rank (
                                    id, rank_name, rank_code, rank_description, node_penalty, order_no,
                                    rank_level, real_flag, hotel_standard, meal_standard,
                                    salary_from, salary_to, enable,
                                    gmt_create_by, gmt_create_time, gmt_modify_by, gmt_modify_time
                                ) VALUES (
                                    :id, :rank_name, :rank_code, :rank_description, :node_penalty, :order_no,
                                    :rank_level, :real_flag, :hotel_standard, :meal_standard,
                                    :salary_from, :salary_to, :enable,
                                    :gmt_create_by, :gmt_create_time, :gmt_modify_by, :gmt_modify_time
                                )
                            """),
                            row_dict
                        )
                    
                    target_session.commit()
                    logger.info(f"{current_time} 从 {source_address} 同步 oa_rank 表成功，共 {len(source_data)} 条记录")
                    return True
                    
                except Exception as e:
                    target_session.rollback()
                    logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（目标数据库操作失败: {str(e)}）")
                    return False
                finally:
                    target_session.close()
                    target_engine.dispose()
                    
            except Exception as e:
                logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库查询失败: {str(e)}）")
                return False
            finally:
                source_session.close()
                source_engine.dispose()
                
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（连接失败: {str(e)}）")
            return False

    @classmethod
    async def sync_oa_employee_primary(cls) -> bool:
        """
        同步 oa_employee_primary 表（全量更新，只同步 company_id=2 的数据）
        
        :return: 是否成功
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            
            # 检查源数据库配置
            if not SourceDataBaseConfig.source_db_host or SourceDataBaseConfig.source_db_host == "placeholder_host":
                logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库配置未设置）")
                return False
            
            # 连接源数据库
            source_engine = create_engine(cls._get_source_db_url(), pool_pre_ping=True)
            source_session = sessionmaker(bind=source_engine)()
            
            try:
                # 从源数据库查询 company_id=2 的数据
                query = text("SELECT * FROM oa_employee_primary WHERE company_id = 2")
                source_data = source_session.execute(query).fetchall()
                
                if not source_data:
                    logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（oa_employee_primary 表无 company_id=2 的数据）")
                    return False
                
                # 连接目标数据库
                target_engine = create_engine(cls._get_target_db_url(), pool_pre_ping=True)
                target_session = sessionmaker(bind=target_engine)()
                
                try:
                    # 全量更新：先删除 company_id=2 的数据，再插入新数据
                    target_session.execute(text("DELETE FROM oa_employee_primary WHERE company_id = 2"))
                    
                    # 插入新数据（需要构建完整的 INSERT 语句，因为字段很多）
                    # 这里使用批量插入的方式
                    for row in source_data:
                        row_dict = dict(row._mapping)
                        # 构建字段名和值的占位符
                        columns = list(row_dict.keys())
                        values_placeholder = ', '.join([f':{col}' for col in columns])
                        columns_str = ', '.join(columns)
                        
                        target_session.execute(
                            text(f"INSERT INTO oa_employee_primary ({columns_str}) VALUES ({values_placeholder})"),
                            row_dict
                        )
                    
                    target_session.commit()
                    logger.info(f"{current_time} 从 {source_address} 同步 oa_employee_primary 表成功，共 {len(source_data)} 条记录（company_id=2）")
                    return True
                    
                except Exception as e:
                    target_session.rollback()
                    logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（目标数据库操作失败: {str(e)}）")
                    return False
                finally:
                    target_session.close()
                    target_engine.dispose()
                    
            except Exception as e:
                logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库查询失败: {str(e)}）")
                return False
            finally:
                source_session.close()
                source_engine.dispose()
                
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（连接失败: {str(e)}）")
            return False

    @classmethod
    async def sync_oa_department(cls) -> bool:
        """
        同步 oa_department 表（全量更新，只同步 code 以 '02' 开头的数据，包括 '02' 本身）
        
        :return: 是否成功
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            
            # 检查源数据库配置
            if not SourceDataBaseConfig.source_db_host or SourceDataBaseConfig.source_db_host == "placeholder_host":
                logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库配置未设置）")
                return False
            
            # 连接源数据库
            source_engine = create_engine(cls._get_source_db_url(), pool_pre_ping=True)
            source_session = sessionmaker(bind=source_engine)()
            
            try:
                # 从源数据库查询 code 以 '02' 开头的数据（包括 '02' 本身）
                query = text("SELECT * FROM oa_department WHERE code LIKE '02%'")
                source_data = source_session.execute(query).fetchall()
                
                if not source_data:
                    logger.warning(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（oa_department 表无 code 以 '02' 开头的数据）")
                    return False
                
                # 连接目标数据库
                target_engine = create_engine(cls._get_target_db_url(), pool_pre_ping=True)
                target_session = sessionmaker(bind=target_engine)()
                
                try:
                    # 全量更新：先删除 code 以 '02' 开头的数据，再插入新数据
                    target_session.execute(text("DELETE FROM oa_department WHERE code LIKE '02%'"))
                    
                    # 插入新数据
                    for row in source_data:
                        row_dict = dict(row._mapping)
                        # 构建字段名和值的占位符
                        columns = list(row_dict.keys())
                        values_placeholder = ', '.join([f':{col}' for col in columns])
                        columns_str = ', '.join(columns)
                        
                        target_session.execute(
                            text(f"INSERT INTO oa_department ({columns_str}) VALUES ({values_placeholder})"),
                            row_dict
                        )
                    
                    target_session.commit()
                    logger.info(f"{current_time} 从 {source_address} 同步 oa_department 表成功，共 {len(source_data)} 条记录（code 以 '02' 开头）")
                    return True
                    
                except Exception as e:
                    target_session.rollback()
                    logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（目标数据库操作失败: {str(e)}）")
                    return False
                finally:
                    target_session.close()
                    target_engine.dispose()
                    
            except Exception as e:
                logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（源数据库查询失败: {str(e)}）")
                return False
            finally:
                source_session.close()
                source_engine.dispose()
                
        except Exception as e:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            source_address = f"{SourceDataBaseConfig.source_db_host}:{SourceDataBaseConfig.source_db_port}/{SourceDataBaseConfig.source_db_database}"
            logger.error(f"{current_time} 从 {source_address} 试图获取数据，结果：失败（连接失败: {str(e)}）")
            return False

    @classmethod
    async def sync_all_tables(cls) -> Dict[str, bool]:
        """
        同步所有表
        
        :return: 同步结果字典
        """
        results = {
            'oa_rank': await cls.sync_oa_rank(),
            'oa_employee_primary': await cls.sync_oa_employee_primary(),
            'oa_department': await cls.sync_oa_department(),
        }
        return results
