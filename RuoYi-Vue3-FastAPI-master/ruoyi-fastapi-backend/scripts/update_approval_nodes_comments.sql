-- ============================================
-- 更新审批节点相关字段注释
-- 将"岗位ID"更正为"编制ID"
-- 执行日期：2025-01-17
-- ============================================

-- MySQL版本
-- 更新 proj_task 表
ALTER TABLE proj_task MODIFY COLUMN approval_nodes TEXT NULL COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';

-- 更新 todo_task 表
ALTER TABLE todo_task MODIFY COLUMN approval_nodes TEXT NULL COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';

-- 更新 apply_rules 表
ALTER TABLE apply_rules MODIFY COLUMN approval_nodes TEXT NULL COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';
ALTER TABLE apply_rules MODIFY COLUMN approved_nodes TEXT NULL COMMENT '已审批节点数组（JSON格式，存储已审批的编制ID列表，oa_department.id）';
ALTER TABLE apply_rules MODIFY COLUMN current_approval_node BIGINT(20) NULL COMMENT '当前审批节点（编制ID，oa_department.id，可为null）';

-- 更新 apply_log 表
ALTER TABLE apply_log MODIFY COLUMN approval_node BIGINT(20) NOT NULL COMMENT '审批节点（编制ID，oa_department.id）';

-- PostgreSQL版本（注释掉，如需使用请取消注释）
/*
-- 更新 proj_task 表
COMMENT ON COLUMN proj_task.approval_nodes IS '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';

-- 更新 todo_task 表
COMMENT ON COLUMN todo_task.approval_nodes IS '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';

-- 更新 apply_rules 表
COMMENT ON COLUMN apply_rules.approval_nodes IS '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';
COMMENT ON COLUMN apply_rules.approved_nodes IS '已审批节点数组（JSON格式，存储已审批的编制ID列表，oa_department.id）';
COMMENT ON COLUMN apply_rules.current_approval_node IS '当前审批节点（编制ID，oa_department.id，可为null）';

-- 更新 apply_log 表
COMMENT ON COLUMN apply_log.approval_node IS '审批节点（编制ID，oa_department.id）';
*/
