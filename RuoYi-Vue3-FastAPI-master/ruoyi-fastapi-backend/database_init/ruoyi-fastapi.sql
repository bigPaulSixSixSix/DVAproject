-- ============================================
-- RuoYi-FastAPI 数据库初始化脚本
-- ============================================
-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (x86_64)
--
-- Host: 127.0.0.1    Database: ruoyi-fastapi
-- ------------------------------------------------------
-- Server version	8.0.43

-- ============================================
-- 创建数据库（如果不存在）
-- ============================================
CREATE DATABASE IF NOT EXISTS `ruoyi-fastapi` 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 使用数据库
USE `ruoyi-fastapi`;

-- ============================================
-- 设置SQL模式和环境变量
-- ============================================
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apply_log`
--

DROP TABLE IF EXISTS `apply_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apply_log` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `apply_id` varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）',
  `approval_node` bigint NOT NULL COMMENT '审批节点（编制ID，oa_department.id）',
  `approver_id` varchar(64) NOT NULL COMMENT '审批人工号',
  `approval_result` int NOT NULL COMMENT '审批结果（0-申请提交，1-同意，2-驳回）',
  `approval_comment` text COMMENT '审批意见',
  `approval_images` text COMMENT '审批意见附图（JSON格式，存储图片URL列表）',
  `approval_start_time` datetime DEFAULT NULL COMMENT '审批开始时间',
  `approval_end_time` datetime DEFAULT NULL COMMENT '审批结束时间',
  PRIMARY KEY (`id`),
  KEY `idx_apply_id` (`apply_id`),
  KEY `idx_approval_node` (`approval_node`),
  KEY `idx_approver_id` (`approver_id`),
  KEY `idx_approval_result` (`approval_result`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='审批日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apply_primary`
--

DROP TABLE IF EXISTS `apply_primary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apply_primary` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `apply_type` int NOT NULL COMMENT '申请类型（1-项目推进任务）',
  `apply_id` varchar(64) NOT NULL COMMENT '申请单ID（雪花算法生成，全局唯一）',
  `apply_status` int NOT NULL DEFAULT '0' COMMENT '申请单状态（0-审批中，1-完成，2-驳回，3-撤销）',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_apply_id` (`apply_id`),
  KEY `idx_apply_type_status` (`apply_type`,`apply_status`),
  KEY `idx_apply_status` (`apply_status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='申请主表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apply_rules`
--

DROP TABLE IF EXISTS `apply_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apply_rules` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `apply_id` varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）',
  `approval_nodes` text COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）',
  `approved_nodes` text COMMENT '已审批节点数组（JSON格式，存储已审批的编制ID列表，oa_department.id）',
  `current_approval_node` bigint DEFAULT NULL COMMENT '当前审批节点（编制ID，oa_department.id，可为null）',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_apply_id` (`apply_id`),
  KEY `idx_current_approval_node` (`current_approval_node`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='审批规则表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apscheduler_jobs`
--

DROP TABLE IF EXISTS `apscheduler_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gen_table`
--

DROP TABLE IF EXISTS `gen_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gen_table` (
  `table_id` bigint NOT NULL AUTO_INCREMENT COMMENT '编号',
  `table_name` varchar(200) DEFAULT '' COMMENT '表名称',
  `table_comment` varchar(500) DEFAULT '' COMMENT '表描述',
  `sub_table_name` varchar(64) DEFAULT NULL COMMENT '关联子表的表名',
  `sub_table_fk_name` varchar(64) DEFAULT NULL COMMENT '子表关联的外键名',
  `class_name` varchar(100) DEFAULT '' COMMENT '实体类名称',
  `tpl_category` varchar(200) DEFAULT 'crud' COMMENT '使用的模板（crud单表操作 tree树表操作）',
  `tpl_web_type` varchar(30) DEFAULT '' COMMENT '前端模板类型（element-ui模版 element-plus模版）',
  `package_name` varchar(100) DEFAULT NULL COMMENT '生成包路径',
  `module_name` varchar(30) DEFAULT NULL COMMENT '生成模块名',
  `business_name` varchar(30) DEFAULT NULL COMMENT '生成业务名',
  `function_name` varchar(50) DEFAULT NULL COMMENT '生成功能名',
  `function_author` varchar(50) DEFAULT NULL COMMENT '生成功能作者',
  `gen_type` char(1) DEFAULT '0' COMMENT '生成代码方式（0zip压缩包 1自定义路径）',
  `gen_path` varchar(200) DEFAULT '/' COMMENT '生成路径（不填默认项目路径）',
  `options` varchar(1000) DEFAULT NULL COMMENT '其它生成选项',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`table_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='代码生成业务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gen_table_column`
--

DROP TABLE IF EXISTS `gen_table_column`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gen_table_column` (
  `column_id` bigint NOT NULL AUTO_INCREMENT COMMENT '编号',
  `table_id` bigint DEFAULT NULL COMMENT '归属表编号',
  `column_name` varchar(200) DEFAULT NULL COMMENT '列名称',
  `column_comment` varchar(500) DEFAULT NULL COMMENT '列描述',
  `column_type` varchar(100) DEFAULT NULL COMMENT '列类型',
  `python_type` varchar(500) DEFAULT NULL COMMENT 'PYTHON类型',
  `python_field` varchar(200) DEFAULT NULL COMMENT 'PYTHON字段名',
  `is_pk` char(1) DEFAULT NULL COMMENT '是否主键（1是）',
  `is_increment` char(1) DEFAULT NULL COMMENT '是否自增（1是）',
  `is_required` char(1) DEFAULT NULL COMMENT '是否必填（1是）',
  `is_unique` char(1) DEFAULT NULL COMMENT '是否唯一（1是）',
  `is_insert` char(1) DEFAULT NULL COMMENT '是否为插入字段（1是）',
  `is_edit` char(1) DEFAULT NULL COMMENT '是否编辑字段（1是）',
  `is_list` char(1) DEFAULT NULL COMMENT '是否列表字段（1是）',
  `is_query` char(1) DEFAULT NULL COMMENT '是否查询字段（1是）',
  `query_type` varchar(200) DEFAULT 'EQ' COMMENT '查询方式（等于、不等于、大于、小于、范围）',
  `html_type` varchar(200) DEFAULT NULL COMMENT '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）',
  `dict_type` varchar(200) DEFAULT '' COMMENT '字典类型',
  `sort` int DEFAULT NULL COMMENT '排序',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`column_id`),
  KEY `table_id` (`table_id`),
  CONSTRAINT `gen_table_column_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `gen_table` (`table_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='代码生成业务表字段';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oa_department`
--

DROP TABLE IF EXISTS `oa_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oa_department` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(100) DEFAULT '' COMMENT '部门名称',
  `code` varchar(50) DEFAULT '' COMMENT '部门代码',
  `parent_id` bigint DEFAULT '0' COMMENT '父部门ID',
  `description` varchar(255) DEFAULT '' COMMENT '描述',
  `sort_no` int DEFAULT '0' COMMENT '排序号',
  `area_id` bigint DEFAULT '0' COMMENT '区域ID',
  `project_id` bigint DEFAULT '0' COMMENT '项目ID',
  `rank_id` bigint DEFAULT '0' COMMENT '职级ID',
  `formation_type` tinyint(1) DEFAULT '0' COMMENT '编制类型',
  `linked_subject_id` bigint DEFAULT '0' COMMENT '关联科目ID',
  `attendance_type` tinyint(1) DEFAULT '0' COMMENT '考勤类型',
  `max_shift_count` int DEFAULT '1' COMMENT '最大班次数',
  `belong_shop_item_ids` varchar(500) DEFAULT '' COMMENT '所属门店项目IDs',
  `post_type` tinyint(1) DEFAULT '0' COMMENT '岗位类型',
  `position_biz_type` tinyint(1) DEFAULT '0' COMMENT '职位业务类型',
  `status` tinyint(1) DEFAULT '0' COMMENT '状态',
  `enable` tinyint(1) DEFAULT '1' COMMENT '启用状态',
  `gmt_create_by` varchar(64) DEFAULT '' COMMENT '创建人',
  `gmt_create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `gmt_modify_by` varchar(64) DEFAULT '' COMMENT '修改人',
  `gmt_modify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_code` (`code`),
  KEY `idx_rank_id` (`rank_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='部门表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oa_employee_primary`
--

DROP TABLE IF EXISTS `oa_employee_primary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oa_employee_primary` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(50) DEFAULT '' COMMENT '姓名',
  `job_number` varchar(20) DEFAULT '' COMMENT '工号',
  `internet_number` varchar(20) DEFAULT '' COMMENT '网络编号',
  `identity_number` varchar(18) DEFAULT '' COMMENT '身份证号',
  `company_id` bigint DEFAULT '0' COMMENT '公司ID',
  `organization_id` bigint DEFAULT '0' COMMENT '组织ID',
  `rank_id` bigint DEFAULT '0' COMMENT '职级ID',
  `status` tinyint(1) DEFAULT '0' COMMENT '状态',
  `phone` varchar(20) DEFAULT '' COMMENT '手机号',
  `job_type` tinyint(1) DEFAULT '0' COMMENT '工作类型',
  `special_work_type` tinyint(1) DEFAULT '0' COMMENT '特殊工作类型',
  `push_id` varchar(100) DEFAULT '' COMMENT '推送ID',
  `bma_push_id` varchar(100) DEFAULT '' COMMENT 'BMA推送ID',
  `agree_policy_flag` tinyint(1) DEFAULT '0' COMMENT '同意政策标志',
  `avatar_image` varchar(500) DEFAULT '' COMMENT '头像图片',
  `sex` tinyint(1) DEFAULT '0' COMMENT '性别(1男2女)',
  `resign_status` tinyint(1) DEFAULT '0' COMMENT '离职状态',
  `entry_date` datetime DEFAULT NULL COMMENT '入职日期',
  `variable_entry_date` datetime DEFAULT NULL COMMENT '可变入职日期',
  `correction_date` datetime DEFAULT NULL COMMENT '转正日期',
  `resign_date` datetime DEFAULT NULL COMMENT '离职日期',
  `attendance_type` tinyint(1) DEFAULT '0' COMMENT '考勤类型',
  `formation_type` tinyint(1) DEFAULT '0' COMMENT '编制类型',
  `salary_type` tinyint(1) DEFAULT '0' COMMENT '薪资类型',
  `unit_salary` decimal(10,2) DEFAULT '0.00' COMMENT '单位薪资',
  `birthday` varchar(10) DEFAULT '' COMMENT '生日',
  `sales_department_id` bigint DEFAULT '0' COMMENT '销售部门ID',
  `sales_status` tinyint(1) DEFAULT '0' COMMENT '销售状态',
  `sales_rank_id` bigint DEFAULT '0' COMMENT '销售职级ID',
  `protocol_expiration_time` datetime DEFAULT NULL COMMENT '协议到期时间',
  `interviewer_job_number` varchar(20) DEFAULT '' COMMENT '面试员工号',
  `special_type` tinyint(1) DEFAULT '0' COMMENT '特殊类型',
  `reserve_flag` tinyint(1) DEFAULT '0' COMMENT '储备标志',
  `protocol_type` tinyint(1) DEFAULT '0' COMMENT '协议类型',
  `important_flag` tinyint(1) DEFAULT '0' COMMENT '重要标志',
  `study_system_flag` tinyint(1) DEFAULT '0' COMMENT '学习系统标志',
  `performance_flag` tinyint(1) DEFAULT '0' COMMENT '绩效标志',
  `enable` tinyint(1) DEFAULT '1' COMMENT '启用状态',
  `gmt_create_by` varchar(64) DEFAULT '' COMMENT '创建人',
  `gmt_create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `gmt_modify_by` varchar(64) DEFAULT '' COMMENT '修改人',
  `gmt_modify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_job_number` (`job_number`),
  KEY `idx_organization_id` (`organization_id`),
  KEY `idx_rank_id` (`rank_id`),
  KEY `idx_company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工主表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oa_rank`
--

DROP TABLE IF EXISTS `oa_rank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oa_rank` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `rank_name` varchar(50) DEFAULT '' COMMENT '职级名称',
  `rank_code` varchar(50) DEFAULT '' COMMENT '职级代码',
  `rank_description` varchar(255) DEFAULT '' COMMENT '职级描述',
  `node_penalty` int DEFAULT '0' COMMENT '节点处罚',
  `order_no` int DEFAULT '0' COMMENT '排序号',
  `rank_level` varchar(10) DEFAULT '' COMMENT '职级等级',
  `real_flag` tinyint(1) DEFAULT '1' COMMENT '真实标志',
  `hotel_standard` decimal(10,2) DEFAULT '0.00' COMMENT '酒店标准',
  `meal_standard` decimal(10,2) DEFAULT '0.00' COMMENT '餐费标准',
  `salary_from` decimal(10,2) DEFAULT '0.00' COMMENT '薪资范围-起始',
  `salary_to` decimal(10,2) DEFAULT '0.00' COMMENT '薪资范围-结束',
  `enable` tinyint(1) DEFAULT '1' COMMENT '启用状态',
  `gmt_create_by` varchar(64) DEFAULT '' COMMENT '创建人',
  `gmt_create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `gmt_modify_by` varchar(64) DEFAULT '' COMMENT '修改人',
  `gmt_modify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_rank_code` (`rank_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='职级表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proj_stage`
--

DROP TABLE IF EXISTS `proj_stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proj_stage` (
  `stage_id` bigint NOT NULL AUTO_INCREMENT COMMENT '阶段ID（主键，自增）',
  `project_id` bigint NOT NULL COMMENT '所属项目ID',
  `name` varchar(200) NOT NULL COMMENT '阶段名称',
  `start_time` date DEFAULT NULL,
  `end_time` date DEFAULT NULL,
  `duration` int DEFAULT NULL COMMENT '持续天数',
  `predecessor_stages` text COMMENT '前置阶段ID列表（JSON格式）',
  `successor_stages` text COMMENT '后置阶段ID列表（JSON格式）',
  `position` text COMMENT '阶段位置信息（JSON格式，包含x、y、height等）',
  `enable` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0' COMMENT '有效性（1有效 0无效，用于软删除）',
  `create_by` varchar(64) DEFAULT '''''' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '''''' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`stage_id`),
  KEY `idx_proj_stage_project_enable` (`project_id`,`enable`),
  KEY `idx_proj_stage_project_id` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='项目阶段表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proj_task`
--

DROP TABLE IF EXISTS `proj_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proj_task` (
  `task_id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务ID（主键，自增）',
  `project_id` bigint NOT NULL COMMENT '所属项目ID',
  `stage_id` bigint DEFAULT NULL COMMENT '所属阶段ID（可为空，表示未归属阶段）',
  `name` varchar(200) NOT NULL COMMENT '任务名称',
  `description` text COMMENT '任务描述',
  `start_time` date DEFAULT NULL,
  `end_time` date DEFAULT NULL,
  `duration` int DEFAULT NULL COMMENT '持续天数',
  `job_number` varchar(64) DEFAULT NULL COMMENT '负责人工号',
  `approval_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）',
  `predecessor_tasks` text COMMENT '前置任务ID列表（JSON格式）',
  `successor_tasks` text COMMENT '后置任务ID列表（JSON格式）',
  `position` text COMMENT '任务位置信息（JSON格式，包含x、y等）',
  `enable` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0' COMMENT '有效性（1有效 0无效，用于软删除）',
  `create_by` varchar(64) DEFAULT '''''' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '''''' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `approval_nodes` text COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）',
  PRIMARY KEY (`task_id`),
  KEY `idx_proj_task_project_id` (`project_id`),
  KEY `idx_proj_task_project_enable` (`project_id`,`enable`),
  KEY `idx_proj_task_stage_id` (`stage_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='项目任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_config`
--

DROP TABLE IF EXISTS `sys_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_config` (
  `config_id` int NOT NULL AUTO_INCREMENT COMMENT '参数主键',
  `config_name` varchar(100) DEFAULT '' COMMENT '参数名称',
  `config_key` varchar(100) DEFAULT '' COMMENT '参数键名',
  `config_value` varchar(500) DEFAULT '' COMMENT '参数键值',
  `config_type` char(1) DEFAULT 'N' COMMENT '系统内置（Y是 N否）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='参数配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_dict_data`
--

DROP TABLE IF EXISTS `sys_dict_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dict_data` (
  `dict_code` bigint NOT NULL AUTO_INCREMENT COMMENT '字典编码',
  `dict_sort` int DEFAULT '0' COMMENT '字典排序',
  `dict_label` varchar(100) DEFAULT '' COMMENT '字典标签',
  `dict_value` varchar(100) DEFAULT '' COMMENT '字典键值',
  `dict_type` varchar(100) DEFAULT '' COMMENT '字典类型',
  `css_class` varchar(100) DEFAULT NULL COMMENT '样式属性（其他样式扩展）',
  `list_class` varchar(100) DEFAULT NULL COMMENT '表格回显样式',
  `is_default` char(1) DEFAULT 'N' COMMENT '是否默认（Y是 N否）',
  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`dict_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_dict_type`
--

DROP TABLE IF EXISTS `sys_dict_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dict_type` (
  `dict_id` bigint NOT NULL AUTO_INCREMENT COMMENT '字典主键',
  `dict_name` varchar(100) DEFAULT '' COMMENT '字典名称',
  `dict_type` varchar(100) DEFAULT '' COMMENT '字典类型',
  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`dict_id`),
  UNIQUE KEY `dict_type` (`dict_type`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典类型表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_job`
--

DROP TABLE IF EXISTS `sys_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_job` (
  `job_id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `job_name` varchar(64) NOT NULL DEFAULT '' COMMENT '任务名称',
  `job_group` varchar(64) NOT NULL DEFAULT 'default' COMMENT '任务组名',
  `job_executor` varchar(64) DEFAULT 'default' COMMENT '任务执行器',
  `invoke_target` varchar(500) NOT NULL COMMENT '调用目标字符串',
  `job_args` varchar(255) DEFAULT '' COMMENT '位置参数',
  `job_kwargs` varchar(255) DEFAULT '' COMMENT '关键字参数',
  `cron_expression` varchar(255) DEFAULT '' COMMENT 'cron执行表达式',
  `misfire_policy` varchar(20) DEFAULT '3' COMMENT '计划执行错误策略（1立即执行 2执行一次 3放弃执行）',
  `concurrent` char(1) DEFAULT '1' COMMENT '是否并发执行（0允许 1禁止）',
  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1暂停）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT '' COMMENT '备注信息',
  PRIMARY KEY (`job_id`,`job_name`,`job_group`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='定时任务调度表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_job_log`
--

DROP TABLE IF EXISTS `sys_job_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_job_log` (
  `job_log_id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务日志ID',
  `job_name` varchar(64) NOT NULL COMMENT '任务名称',
  `job_group` varchar(64) NOT NULL COMMENT '任务组名',
  `job_executor` varchar(64) NOT NULL COMMENT '任务执行器',
  `invoke_target` varchar(500) NOT NULL COMMENT '调用目标字符串',
  `job_args` varchar(255) DEFAULT '' COMMENT '位置参数',
  `job_kwargs` varchar(255) DEFAULT '' COMMENT '关键字参数',
  `job_trigger` varchar(255) DEFAULT '' COMMENT '任务触发器',
  `job_message` varchar(500) DEFAULT NULL COMMENT '日志信息',
  `status` char(1) DEFAULT '0' COMMENT '执行状态（0正常 1失败）',
  `exception_info` varchar(2000) DEFAULT '' COMMENT '异常信息',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`job_log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='定时任务调度日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_logininfor`
--

DROP TABLE IF EXISTS `sys_logininfor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_logininfor` (
  `info_id` bigint NOT NULL AUTO_INCREMENT COMMENT '访问ID',
  `user_name` varchar(50) DEFAULT '' COMMENT '用户账号',
  `ipaddr` varchar(128) DEFAULT '' COMMENT '登录IP地址',
  `login_location` varchar(255) DEFAULT '' COMMENT '登录地点',
  `browser` varchar(50) DEFAULT '' COMMENT '浏览器类型',
  `os` varchar(50) DEFAULT '' COMMENT '操作系统',
  `status` char(1) DEFAULT '0' COMMENT '登录状态（0成功 1失败）',
  `msg` varchar(255) DEFAULT '' COMMENT '提示消息',
  `login_time` datetime DEFAULT NULL COMMENT '访问时间',
  PRIMARY KEY (`info_id`),
  KEY `idx_sys_logininfor_s` (`status`),
  KEY `idx_sys_logininfor_lt` (`login_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统访问记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_menu`
--

DROP TABLE IF EXISTS `sys_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_menu` (
  `menu_id` bigint NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
  `menu_name` varchar(50) NOT NULL COMMENT '菜单名称',
  `parent_id` bigint DEFAULT '0' COMMENT '父菜单ID',
  `order_num` int DEFAULT '0' COMMENT '显示顺序',
  `path` varchar(200) DEFAULT '' COMMENT '路由地址',
  `component` varchar(255) DEFAULT NULL COMMENT '组件路径',
  `query` varchar(255) DEFAULT NULL COMMENT '路由参数',
  `route_name` varchar(50) DEFAULT '' COMMENT '路由名称',
  `is_frame` int DEFAULT '1' COMMENT '是否为外链（0是 1否）',
  `is_cache` int DEFAULT '0' COMMENT '是否缓存（0缓存 1不缓存）',
  `menu_type` char(1) DEFAULT '' COMMENT '菜单类型（M目录 C菜单 F按钮）',
  `visible` char(1) DEFAULT '0' COMMENT '菜单状态（0显示 1隐藏）',
  `status` char(1) DEFAULT '0' COMMENT '菜单状态（0正常 1停用）',
  `perms` varchar(100) DEFAULT NULL COMMENT '权限标识',
  `icon` varchar(100) DEFAULT '#' COMMENT '菜单图标',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT '' COMMENT '备注',
  PRIMARY KEY (`menu_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='菜单权限表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_notice`
--

DROP TABLE IF EXISTS `sys_notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_notice` (
  `notice_id` int NOT NULL AUTO_INCREMENT COMMENT '公告ID',
  `notice_title` varchar(50) NOT NULL COMMENT '公告标题',
  `notice_type` char(1) NOT NULL COMMENT '公告类型（1通知 2公告）',
  `notice_content` longblob COMMENT '公告内容',
  `status` char(1) DEFAULT '0' COMMENT '公告状态（0正常 1关闭）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`notice_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='通知公告表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_oper_log`
--

DROP TABLE IF EXISTS `sys_oper_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_oper_log` (
  `oper_id` bigint NOT NULL AUTO_INCREMENT COMMENT '日志主键',
  `title` varchar(50) DEFAULT '' COMMENT '模块标题',
  `business_type` int DEFAULT '0' COMMENT '业务类型（0其它 1新增 2修改 3删除）',
  `method` varchar(100) DEFAULT '' COMMENT '方法名称',
  `request_method` varchar(10) DEFAULT '' COMMENT '请求方式',
  `operator_type` int DEFAULT '0' COMMENT '操作类别（0其它 1后台用户 2手机端用户）',
  `oper_name` varchar(50) DEFAULT '' COMMENT '操作人员',
  `dept_name` varchar(50) DEFAULT '' COMMENT '部门名称',
  `oper_url` varchar(255) DEFAULT '' COMMENT '请求URL',
  `oper_ip` varchar(128) DEFAULT '' COMMENT '主机地址',
  `oper_location` varchar(255) DEFAULT '' COMMENT '操作地点',
  `oper_param` varchar(2000) DEFAULT '' COMMENT '请求参数',
  `json_result` varchar(2000) DEFAULT '' COMMENT '返回参数',
  `status` int DEFAULT '0' COMMENT '操作状态（0正常 1异常）',
  `error_msg` varchar(2000) DEFAULT '' COMMENT '错误消息',
  `oper_time` datetime DEFAULT NULL COMMENT '操作时间',
  `cost_time` bigint DEFAULT '0' COMMENT '消耗时间',
  PRIMARY KEY (`oper_id`),
  KEY `idx_sys_oper_log_bt` (`business_type`),
  KEY `idx_sys_oper_log_s` (`status`),
  KEY `idx_sys_oper_log_ot` (`oper_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='操作日志记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role`
--

DROP TABLE IF EXISTS `sys_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role` (
  `role_id` bigint NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `role_name` varchar(30) NOT NULL COMMENT '角色名称',
  `role_key` varchar(100) NOT NULL COMMENT '角色权限字符串',
  `role_sort` int NOT NULL COMMENT '显示顺序',
  `data_scope` char(1) DEFAULT '1' COMMENT '数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）',
  `menu_check_strictly` tinyint(1) DEFAULT '1' COMMENT '菜单树选择项是否关联显示',
  `dept_check_strictly` tinyint(1) DEFAULT '1' COMMENT '部门树选择项是否关联显示',
  `status` char(1) NOT NULL COMMENT '角色状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role_dept`
--

DROP TABLE IF EXISTS `sys_role_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role_dept` (
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `dept_id` bigint NOT NULL COMMENT '部门ID',
  PRIMARY KEY (`role_id`,`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色和部门关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role_menu`
--

DROP TABLE IF EXISTS `sys_role_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role_menu` (
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `menu_id` bigint NOT NULL COMMENT '菜单ID',
  PRIMARY KEY (`role_id`,`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色和菜单关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `user_id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `dept_id` bigint DEFAULT NULL COMMENT '部门ID',
  `user_name` varchar(30) NOT NULL COMMENT '用户账号',
  `nick_name` varchar(30) NOT NULL COMMENT '用户昵称',
  `user_type` varchar(2) DEFAULT '00' COMMENT '用户类型（00系统用户）',
  `email` varchar(50) DEFAULT '''''' COMMENT '用户邮箱',
  `phonenumber` varchar(11) DEFAULT '''''' COMMENT '手机号码',
  `sex` char(1) DEFAULT '0' COMMENT '用户性别（0男 1女 2未知）',
  `avatar` varchar(100) DEFAULT '''''' COMMENT '头像地址',
  `password` varchar(100) DEFAULT '''''' COMMENT '密码',
  `status` char(1) DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `login_ip` varchar(128) DEFAULT '''''' COMMENT '最后登录IP',
  `login_date` datetime DEFAULT NULL COMMENT '最后登录时间',
  `pwd_update_date` datetime DEFAULT NULL COMMENT '密码最后更新时间',
  `create_by` varchar(64) DEFAULT '''''' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '''''' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_local`
--

DROP TABLE IF EXISTS `sys_user_local`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_local` (
  `user_id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户ID（本地主键）',
  `employee_id` bigint NOT NULL COMMENT '员工ID（关联 oa_employee_primary.id）',
  `job_number` varchar(20) NOT NULL COMMENT '工号（登录账号）',
  `password` varchar(100) DEFAULT '''''' COMMENT '密码',
  `status` char(1) DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `enable` char(1) DEFAULT '1' COMMENT '启用状态（0禁用 1启用）',
  `login_ip` varchar(128) DEFAULT '''''' COMMENT '最后登录IP',
  `login_date` datetime DEFAULT NULL COMMENT '最后登录时间',
  `pwd_update_date` datetime DEFAULT NULL COMMENT '密码最后更新时间',
  `sync_time` datetime DEFAULT NULL COMMENT '数据同步时间',
  `create_by` varchar(64) DEFAULT '''''' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '''''' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='本地用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_post`
--

DROP TABLE IF EXISTS `sys_user_post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_post` (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `post_id` bigint NOT NULL COMMENT '岗位ID',
  PRIMARY KEY (`user_id`,`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户与岗位关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_role`
--

DROP TABLE IF EXISTS `sys_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_role` (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `role_id` bigint NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户和角色关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `todo_stage`
--

DROP TABLE IF EXISTS `todo_stage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `todo_stage` (
  `stage_id` bigint NOT NULL COMMENT '阶段ID（关联proj_stage.stage_id，主键）',
  `project_id` bigint NOT NULL COMMENT '项目ID',
  `stage_status` int NOT NULL DEFAULT '0' COMMENT '阶段状态（0-未开始，1-进行中，2-已完成）',
  `predecessor_stages` text COMMENT '前置阶段ID列表（JSON格式）',
  `successor_stages` text COMMENT '后置阶段ID列表（JSON格式）',
  `actual_start_time` datetime DEFAULT NULL COMMENT '实际开始时间',
  `actual_complete_time` datetime DEFAULT NULL COMMENT '实际完成时间',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`stage_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_stage_status` (`stage_status`),
  KEY `idx_project_status` (`project_id`,`stage_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='阶段执行表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `todo_task`
--

DROP TABLE IF EXISTS `todo_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `todo_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` bigint NOT NULL COMMENT '任务ID（关联proj_task.task_id）',
  `project_id` bigint NOT NULL COMMENT '项目ID',
  `stage_id` bigint DEFAULT NULL COMMENT '阶段ID',
  `name` varchar(200) NOT NULL COMMENT '任务名称',
  `description` text COMMENT '任务描述',
  `start_time` date DEFAULT NULL COMMENT '开始日期',
  `end_time` date DEFAULT NULL COMMENT '结束日期',
  `duration` int DEFAULT NULL COMMENT '持续天数',
  `job_number` varchar(64) DEFAULT NULL COMMENT '负责人工号',
  `predecessor_tasks` text COMMENT '前置任务ID列表（JSON格式）',
  `successor_tasks` text COMMENT '后置任务ID列表（JSON格式）',
  `approval_nodes` text COMMENT '审批节点数组（JSON格式，存储编制ID列表，oa_department.id）',
  `task_status` int NOT NULL DEFAULT '0' COMMENT '任务状态（0-未开始，1-进行中，2-已提交，3-完成，4-驳回）',
  `is_skipped` int NOT NULL DEFAULT '0' COMMENT '是否跳过（0-未跳过，1-已跳过）',
  `actual_start_time` datetime DEFAULT NULL COMMENT '实际开始时间',
  `actual_complete_time` datetime DEFAULT NULL COMMENT '实际完成时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_id` (`task_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_stage_id` (`stage_id`),
  KEY `idx_task_status` (`task_status`),
  KEY `idx_project_status` (`project_id`,`task_status`),
  KEY `idx_job_number` (`job_number`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='任务执行表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `todo_task_apply`
--

DROP TABLE IF EXISTS `todo_task_apply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `todo_task_apply` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `apply_id` varchar(64) NOT NULL COMMENT '申请单ID（关联apply_primary.apply_id）',
  `task_id` bigint NOT NULL COMMENT '任务ID（关联todo_task.id）',
  `submit_text` text COMMENT '提交文本',
  `submit_images` text COMMENT '提交图片（JSON格式，存储图片URL列表）',
  `submit_time` datetime DEFAULT NULL COMMENT '提交时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_apply_id` (`apply_id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_submit_time` (`submit_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='任务申请详情表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-12 10:13:40
