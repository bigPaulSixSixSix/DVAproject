-- ============================================
-- 修复 todo_task_apply 表注释和字段注释（解决乱码问题）
-- ============================================

-- 设置字符集
SET NAMES utf8mb4;

-- ----------------------------
-- 任务申请详情表 (todo_task_apply)
-- ----------------------------
ALTER TABLE todo_task_apply COMMENT = '任务申请详情表';
ALTER TABLE todo_task_apply MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';
ALTER TABLE todo_task_apply MODIFY COLUMN apply_id varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）';
ALTER TABLE todo_task_apply MODIFY COLUMN task_id bigint(20) NOT NULL COMMENT '任务ID（关联todo_task.id）';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_text text COMMENT '提交文本';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_images text COMMENT '提交图片（JSON格式，存储图片URL列表）';
ALTER TABLE todo_task_apply MODIFY COLUMN submit_time datetime COMMENT '提交时间';
