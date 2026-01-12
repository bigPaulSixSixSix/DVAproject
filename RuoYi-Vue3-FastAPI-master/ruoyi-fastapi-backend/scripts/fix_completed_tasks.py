"""
修复已完成但任务状态未更新的数据
执行日期：2025-12-29
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from config.database import AsyncSessionLocal
from module_task.entity.do.todo_task_do import TodoTask
from module_task.entity.do.todo_task_apply_do import TodoTaskApply
from module_apply.entity.do.apply_primary_do import ApplyPrimary
from module_apply.entity.do.apply_rules_do import ApplyRules
from utils.log_util import logger
from datetime import datetime


async def fix_completed_tasks():
    """
    修复已完成但任务状态未更新的数据
    条件：申请单状态为完成（1），但任务状态不是完成（3）
    """
    async with AsyncSessionLocal() as db:
        try:
            # 查询需要修复的任务
            # 条件：申请单状态为完成（1），但任务状态不是完成（3）
            query = (
                select(
                    ApplyPrimary.apply_id,
                    TodoTaskApply.task_id.label('todo_task_id'),
                    TodoTask.task_id.label('proj_task_id'),
                    TodoTask.task_status,
                    TodoTask.name
                )
                .select_from(ApplyPrimary)
                .join(TodoTaskApply, ApplyPrimary.apply_id == TodoTaskApply.apply_id)
                .join(TodoTask, TodoTaskApply.task_id == TodoTask.id)
                .where(
                    ApplyPrimary.apply_status == 1,  # 申请单状态为完成
                    TodoTask.task_status != 3  # 但任务状态不是完成
                )
            )
            
            result = await db.execute(query)
            tasks_to_fix = result.all()
            
            if not tasks_to_fix:
                print("没有需要修复的任务")
                return
            
            print(f"找到 {len(tasks_to_fix)} 个需要修复的任务：")
            for row in tasks_to_fix:
                print(f"  - 任务ID: {row.proj_task_id}, 任务名称: {row.name}, 当前状态: {row.task_status}, 申请单ID: {row.apply_id}")
            
            # 验证每个任务的审批流程是否真的已完成
            fixed_count = 0
            skipped_count = 0
            
            for row in tasks_to_fix:
                apply_id = row.apply_id
                proj_task_id = row.proj_task_id
                
                # 检查审批规则，确认审批流程是否真的已完成
                rules_result = await db.execute(
                    select(ApplyRules).where(ApplyRules.apply_id == apply_id)
                )
                rules = rules_result.scalar_one_or_none()
                
                if not rules:
                    print(f"  ⚠ 跳过任务 {proj_task_id}：审批规则不存在")
                    skipped_count += 1
                    continue
                
                # 检查是否所有节点都已审批完成
                # 如果 current_approval_node 为 None，说明审批已完成
                if rules.current_approval_node is not None:
                    print(f"  ⚠ 跳过任务 {proj_task_id}：审批流程未完成（current_approval_node={rules.current_approval_node}）")
                    skipped_count += 1
                    continue
                
                # 确认审批已完成，更新任务状态
                now = datetime.now()
                await db.execute(
                    update(TodoTask)
                    .where(TodoTask.task_id == proj_task_id)
                    .values(
                        task_status=3,  # 完成
                        actual_complete_time=now
                    )
                )
                print(f"  ✓ 修复任务 {proj_task_id}：状态已更新为完成")
                fixed_count += 1
            
            await db.commit()
            
            print()
            print("=" * 60)
            print(f"修复完成！")
            print(f"  修复数量: {fixed_count}")
            print(f"  跳过数量: {skipped_count}")
            print("=" * 60)
            
        except Exception as e:
            await db.rollback()
            logger.error(f'修复任务状态失败: {str(e)}', exc_info=True)
            print(f"修复失败: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(fix_completed_tasks())

