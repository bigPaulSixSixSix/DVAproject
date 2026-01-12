"""
任务模块数据库实体（配置和执行共用）
"""
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.do.todo_stage_do import TodoStage
from module_task.entity.do.todo_task_do import TodoTask
from module_task.entity.do.todo_task_apply_do import TodoTaskApply

__all__ = ['ProjStage', 'ProjTask', 'TodoStage', 'TodoTask', 'TodoTaskApply']
