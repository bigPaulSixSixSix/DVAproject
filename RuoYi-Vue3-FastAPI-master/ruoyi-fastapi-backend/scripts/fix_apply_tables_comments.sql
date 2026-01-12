-- ============================================
-- 修复 apply_rules、apply_log、todo_task 表的字段注释乱码问题
-- 执行日期：2025-12-23
-- ============================================

SET NAMES utf8mb4;

-- ----------------------------
-- 修复 apply_rules 表
-- ----------------------------
ALTER TABLE apply_rules COMMENT = '审批规则表';
ALTER TABLE apply_rules MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE apply_rules MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE apply_rules MODIFY COLUMN approval_nodes text COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';
ALTER TABLE apply_rules MODIFY COLUMN approved_nodes text COMMENT '已审批节点数组（JSON格式，存储已审批的编制ID列表，oa_department.id）';
ALTER TABLE apply_rules MODIFY COLUMN current_approval_node bigint(20) DEFAULT NULL COMMENT '当前审批节点（编制ID，oa_department.id，可为null）';
ALTER TABLE apply_rules MODIFY COLUMN create_time datetime COMMENT '创建时间';
ALTER TABLE apply_rules MODIFY COLUMN update_time datetime COMMENT '更新时间';

-- ----------------------------
-- 修复 apply_log 表
-- ----------------------------
ALTER TABLE apply_log COMMENT = '审批日志表';
ALTER TABLE apply_log MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE apply_log MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE apply_log MODIFY COLUMN approval_node bigint(20) NOT NULL COMMENT '审批节点（编制ID，oa_department.id）';
ALTER TABLE apply_log MODIFY COLUMN approver_id varchar(64) NOT NULL COMMENT '审批人工号';
ALTER TABLE apply_log MODIFY COLUMN approval_result int(4) NOT NULL COMMENT '审批结果（0-申请提交，1-同意，2-驳回）';
ALTER TABLE apply_log MODIFY COLUMN approval_comment text COMMENT '审批意见';
ALTER TABLE apply_log MODIFY COLUMN approval_images text COMMENT '审批意见附图（JSON格式，存储图片URL列表）';
ALTER TABLE apply_log MODIFY COLUMN approval_start_time datetime COMMENT '审批开始时间';
ALTER TABLE apply_log MODIFY COLUMN approval_end_time datetime COMMENT '审批结束时间';

-- ----------------------------
-- 修复 todo_task 表
-- ----------------------------
ALTER TABLE todo_task COMMENT = '任务执行表';
ALTER TABLE todo_task MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE todo_task MODIFY COLUMN task_id bigint(20) NOT NULL COMMENT '任务ID（关联proj_task.task_id）';
ALTER TABLE todo_task MODIFY COLUMN project_id bigint(20) NOT NULL COMMENT '项目ID';
ALTER TABLE todo_task MODIFY COLUMN stage_id bigint(20) DEFAULT NULL COMMENT '阶段ID';
ALTER TABLE todo_task MODIFY COLUMN name varchar(200) NOT NULL COMMENT '任务名称';
ALTER TABLE todo_task MODIFY COLUMN description text COMMENT '任务描述';
ALTER TABLE todo_task MODIFY COLUMN start_time date COMMENT '开始日期';
ALTER TABLE todo_task MODIFY COLUMN end_time date COMMENT '结束日期';
ALTER TABLE todo_task MODIFY COLUMN duration int(4) DEFAULT NULL COMMENT '持续天数';
ALTER TABLE todo_task MODIFY COLUMN job_number varchar(64) DEFAULT NULL COMMENT '负责人工号';
ALTER TABLE todo_task MODIFY COLUMN predecessor_tasks text COMMENT '前置任务ID列表（JSON格式）';
ALTER TABLE todo_task MODIFY COLUMN successor_tasks text COMMENT '后置任务ID列表（JSON格式）';
ALTER TABLE todo_task MODIFY COLUMN approval_nodes text COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）';
ALTER TABLE todo_task MODIFY COLUMN task_status int(4) NOT NULL DEFAULT 0 COMMENT '任务状态（0-未开始，1-进行中，2-已提交，3-完成，4-驳回）';
ALTER TABLE todo_task MODIFY COLUMN is_skipped int(4) NOT NULL DEFAULT 0 COMMENT '是否跳过（0-未跳过，1-已跳过）';
ALTER TABLE todo_task MODIFY COLUMN actual_start_time datetime COMMENT '实际开始时间';
ALTER TABLE todo_task MODIFY COLUMN actual_complete_time datetime COMMENT '实际完成时间';
