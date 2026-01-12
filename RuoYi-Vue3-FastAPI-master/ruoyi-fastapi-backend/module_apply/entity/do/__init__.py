"""
通用申请/审批模块数据库实体
"""
from module_apply.entity.do.apply_primary_do import ApplyPrimary
from module_apply.entity.do.apply_rules_do import ApplyRules
from module_apply.entity.do.apply_log_do import ApplyLog

__all__ = ['ApplyPrimary', 'ApplyRules', 'ApplyLog']
