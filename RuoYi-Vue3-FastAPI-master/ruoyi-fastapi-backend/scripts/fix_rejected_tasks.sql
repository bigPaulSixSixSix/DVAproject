-- ============================================
-- 修复被驳回但任务状态未更新的数据
-- 执行日期：2025-01-17
-- ============================================

-- 查询需要修复的任务（申请单状态为驳回，但任务状态不是驳回）
-- SELECT 
--     ap.apply_id,
--     ap.apply_status,
--     tta.task_id as todo_task_id,
--     tt.task_id as proj_task_id,
--     tt.task_status,
--     tt.name
-- FROM apply_primary ap
-- JOIN todo_task_apply tta ON ap.apply_id = tta.apply_id
-- JOIN todo_task tt ON tta.task_id = tt.id
-- WHERE ap.apply_status = 2  -- 申请单状态为驳回
--   AND tt.task_status != 4;  -- 但任务状态不是驳回

-- 修复：将申请单状态为驳回的任务，更新任务状态为驳回（4）
UPDATE todo_task tt
INNER JOIN todo_task_apply tta ON tt.id = tta.task_id
INNER JOIN apply_primary ap ON tta.apply_id = ap.apply_id
SET tt.task_status = 4  -- 驳回
WHERE ap.apply_status = 2  -- 申请单状态为驳回
  AND tt.task_status != 4;  -- 但任务状态不是驳回

-- 查询修复结果
SELECT 
    '修复后的任务状态' as description,
    COUNT(*) as fixed_count
FROM todo_task tt
INNER JOIN todo_task_apply tta ON tt.id = tta.task_id
INNER JOIN apply_primary ap ON tta.apply_id = ap.apply_id
WHERE ap.apply_status = 2
  AND tt.task_status = 4;
