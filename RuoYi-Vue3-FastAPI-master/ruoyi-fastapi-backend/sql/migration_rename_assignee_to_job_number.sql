-- ============================================
-- 数据库迁移：将 assignee 字段重命名为 job_number
-- 并修复字段备注乱码问题
-- 执行日期：2025-01-17
-- ============================================

-- ----------------------------
-- MySQL版本
-- ----------------------------
-- 1. 重命名字段 assignee -> job_number
ALTER TABLE proj_task CHANGE COLUMN assignee job_number VARCHAR(64) NULL COMMENT '负责人工号';

-- 2. 修复所有字段的备注乱码问题（使用正确的字符集）
ALTER TABLE proj_task MODIFY COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）';
ALTER TABLE proj_task MODIFY COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）';

-- ----------------------------
-- PostgreSQL版本
-- ----------------------------
-- 1. 重命名字段 assignee -> job_number
-- ALTER TABLE proj_task RENAME COLUMN assignee TO job_number;
-- COMMENT ON COLUMN proj_task.job_number IS '负责人工号';

-- 2. 修复所有字段的备注乱码问题
-- COMMENT ON COLUMN proj_task.approval_type IS '审批模式（specified-指定编制审批，sequential-逐级审批）';
-- COMMENT ON COLUMN proj_task.approval_levels IS '审批层级数组（JSON格式，存储岗位编制ID列表）';
