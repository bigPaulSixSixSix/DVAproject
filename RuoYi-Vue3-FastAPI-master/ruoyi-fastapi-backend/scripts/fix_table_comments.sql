-- ============================================
-- 修复表注释和字段注释（解决乱码问题）
-- ============================================

-- 设置字符集
SET NAMES utf8mb4;

-- ----------------------------
-- 1、申请主表 (apply_primary)
-- ----------------------------
ALTER TABLE apply_primary COMMENT = '申请主表';
ALTER TABLE apply_primary MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE apply_primary MODIFY COLUMN apply_type int(4) NOT NULL COMMENT '申请类型（1-项目推进任务）';
ALTER TABLE apply_primary MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（雪花算法生成，全局唯一）';
ALTER TABLE apply_primary MODIFY COLUMN apply_status int(4) NOT NULL DEFAULT 0 COMMENT '申请单状态（0-审批中，1-完成，2-驳回，3-撤销）';
ALTER TABLE apply_primary MODIFY COLUMN create_time datetime COMMENT '创建时间';
ALTER TABLE apply_primary MODIFY COLUMN update_time datetime COMMENT '更新时间';

-- ----------------------------
-- 2、审批规则表 (apply_rules)
-- ----------------------------
ALTER TABLE apply_rules COMMENT = '审批规则表';
ALTER TABLE apply_rules MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE apply_rules MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE apply_rules MODIFY COLUMN approval_nodes text COMMENT '审批节点数组（JSON格式，存储岗位ID列表）';
ALTER TABLE apply_rules MODIFY COLUMN approved_nodes text COMMENT '已审批节点数组（JSON格式，存储已审批的岗位ID列表）';
ALTER TABLE apply_rules MODIFY COLUMN current_approval_node bigint(20) DEFAULT NULL COMMENT '当前审批节点（岗位ID，可为null）';
ALTER TABLE apply_rules MODIFY COLUMN create_time datetime COMMENT '创建时间';
ALTER TABLE apply_rules MODIFY COLUMN update_time datetime COMMENT '更新时间';

-- ----------------------------
-- 3、审批日志表 (apply_log)
-- ----------------------------
ALTER TABLE apply_log COMMENT = '审批日志表';
ALTER TABLE apply_log MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE apply_log MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE apply_log MODIFY COLUMN approval_node bigint(20) NOT NULL COMMENT '审批节点（岗位ID）';
ALTER TABLE apply_log MODIFY COLUMN approver_id varchar(64) NOT NULL COMMENT '审批人工号';
ALTER TABLE apply_log MODIFY COLUMN approval_result int(4) NOT NULL COMMENT '审批结果（0-申请提交，1-同意，2-驳回）';
ALTER TABLE apply_log MODIFY COLUMN approval_comment text COMMENT '审批意见';
ALTER TABLE apply_log MODIFY COLUMN approval_images text COMMENT '审批意见附图（JSON格式，存储图片URL列表）';
ALTER TABLE apply_log MODIFY COLUMN approval_start_time datetime COMMENT '审批开始时间';
ALTER TABLE apply_log MODIFY COLUMN approval_end_time datetime COMMENT '审批结束时间';

-- ----------------------------
-- 4、任务执行表 (todo_task)
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
ALTER TABLE todo_task MODIFY COLUMN assignee varchar(64) DEFAULT NULL COMMENT '负责人（用户ID或用户名）';
ALTER TABLE todo_task MODIFY COLUMN predecessor_tasks text COMMENT '前置任务ID列表（JSON格式）';
ALTER TABLE todo_task MODIFY COLUMN successor_tasks text COMMENT '后置任务ID列表（JSON格式）';
ALTER TABLE todo_task MODIFY COLUMN approval_nodes text COMMENT '审批节点数组（JSON格式，存储岗位ID列表）';
ALTER TABLE todo_task MODIFY COLUMN task_status int(4) NOT NULL DEFAULT 0 COMMENT '任务状态（0-未开始，1-进行中，2-已提交，3-完成，4-驳回）';
ALTER TABLE todo_task MODIFY COLUMN is_skipped int(4) NOT NULL DEFAULT 0 COMMENT '是否跳过（0-未跳过，1-已跳过）';
ALTER TABLE todo_task MODIFY COLUMN actual_start_time datetime COMMENT '实际开始时间';
ALTER TABLE todo_task MODIFY COLUMN actual_complete_time datetime COMMENT '实际完成时间';

-- ----------------------------
-- 5、阶段执行表 (todo_stage)
-- ----------------------------
ALTER TABLE todo_stage COMMENT = '阶段执行表';
ALTER TABLE todo_stage MODIFY COLUMN stage_id bigint(20) NOT NULL COMMENT '阶段ID（关联proj_stage.stage_id，主键）';
ALTER TABLE todo_stage MODIFY COLUMN project_id bigint(20) NOT NULL COMMENT '项目ID';
ALTER TABLE todo_stage MODIFY COLUMN stage_status int(4) NOT NULL DEFAULT 0 COMMENT '阶段状态（0-未开始，1-进行中，2-已完成）';
ALTER TABLE todo_stage MODIFY COLUMN predecessor_stages text COMMENT '前置阶段ID列表（JSON格式）';
ALTER TABLE todo_stage MODIFY COLUMN successor_stages text COMMENT '后置阶段ID列表（JSON格式）';
ALTER TABLE todo_stage MODIFY COLUMN actual_start_time datetime COMMENT '实际开始时间';
ALTER TABLE todo_stage MODIFY COLUMN actual_complete_time datetime COMMENT '实际完成时间';
ALTER TABLE todo_stage MODIFY COLUMN create_time datetime COMMENT '创建时间';
ALTER TABLE todo_stage MODIFY COLUMN update_time datetime COMMENT '更新时间';

-- ----------------------------
-- 6、任务申请详情表 (todo_task_apply)
-- ----------------------------
ALTER TABLE todo_task_apply COMMENT = '任务申请详情表';
ALTER TABLE todo_task_apply MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE todo_task_apply MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE todo_task_apply MODIFY COLUMN task_id bigint(20) NOT NULL COMMENT '任务ID（关联todo_task.id）';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_text text COMMENT '提交文本';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_images text COMMENT '提交图片（JSON格式，存储图片URL列表）';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_time datetime COMMENT '提交时间';
