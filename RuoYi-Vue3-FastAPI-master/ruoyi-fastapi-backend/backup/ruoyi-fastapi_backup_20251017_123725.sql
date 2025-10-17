-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (x86_64)
--
-- Host: localhost    Database: ruoyi-fastapi
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Current Database: `ruoyi-fastapi`
--

/*!40000 DROP DATABASE IF EXISTS `ruoyi-fastapi`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ruoyi-fastapi` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ruoyi-fastapi`;

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
-- Dumping data for table `apscheduler_jobs`
--

LOCK TABLES `apscheduler_jobs` WRITE;
/*!40000 ALTER TABLE `apscheduler_jobs` DISABLE KEYS */;
/*!40000 ALTER TABLE `apscheduler_jobs` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `gen_table`
--

LOCK TABLES `gen_table` WRITE;
/*!40000 ALTER TABLE `gen_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `gen_table` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `gen_table_column`
--

LOCK TABLES `gen_table_column` WRITE;
/*!40000 ALTER TABLE `gen_table_column` DISABLE KEYS */;
/*!40000 ALTER TABLE `gen_table_column` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='参数配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_config`
--

LOCK TABLES `sys_config` WRITE;
/*!40000 ALTER TABLE `sys_config` DISABLE KEYS */;
INSERT INTO `sys_config` (`config_id`, `config_name`, `config_key`, `config_value`, `config_type`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'主框架页-默认皮肤样式名称','sys.index.skinName','skin-blue','Y','admin','2025-10-16 10:32:52','',NULL,'蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow'),(2,'用户管理-账号初始密码','sys.user.initPassword','123456','Y','admin','2025-10-16 10:32:52','',NULL,'初始化密码 123456'),(3,'主框架页-侧边栏主题','sys.index.sideTheme','theme-dark','Y','admin','2025-10-16 10:32:52','',NULL,'深色主题theme-dark，浅色主题theme-light'),(4,'账号自助-验证码开关','sys.account.captchaEnabled','true','Y','admin','2025-10-16 10:32:52','',NULL,'是否开启验证码功能（true开启，false关闭）'),(5,'账号自助-是否开启用户注册功能','sys.account.registerUser','false','Y','admin','2025-10-16 10:32:52','',NULL,'是否开启注册用户功能（true开启，false关闭）'),(6,'用户登录-黑名单列表','sys.login.blackIPList','','Y','admin','2025-10-16 10:32:52','',NULL,'设置登录IP黑名单限制，多个匹配项以;分隔，支持匹配（*通配、网段）'),(7,'用户管理-初始密码修改策略','sys.account.initPasswordModify','1','Y','admin','2025-10-16 10:32:52','',NULL,'0：初始密码修改策略关闭，没有任何提示，1：提醒用户，如果未修改初始密码，则在登录时就会提醒修改密码对话框'),(8,'用户管理-账号密码更新周期','sys.account.passwordValidateDays','0','Y','admin','2025-10-16 10:32:52','',NULL,'密码更新周期（填写数字，数据初始化值为0不限制，若修改必须为大于0小于365的正整数），如果超过这个周期登录系统时，则在登录时就会提醒修改密码对话框');
/*!40000 ALTER TABLE `sys_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dept`
--

DROP TABLE IF EXISTS `sys_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dept` (
  `dept_id` bigint NOT NULL AUTO_INCREMENT COMMENT '部门id',
  `parent_id` bigint DEFAULT '0' COMMENT '父部门id',
  `ancestors` varchar(50) DEFAULT '' COMMENT '祖级列表',
  `dept_name` varchar(30) DEFAULT '' COMMENT '部门名称',
  `order_num` int DEFAULT '0' COMMENT '显示顺序',
  `leader` varchar(20) DEFAULT NULL COMMENT '负责人',
  `phone` varchar(11) DEFAULT NULL COMMENT '联系电话',
  `email` varchar(50) DEFAULT NULL COMMENT '邮箱',
  `status` char(1) DEFAULT '0' COMMENT '部门状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=213 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='部门表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dept`
--

LOCK TABLES `sys_dept` WRITE;
/*!40000 ALTER TABLE `sys_dept` DISABLE KEYS */;
INSERT INTO `sys_dept` (`dept_id`, `parent_id`, `ancestors`, `dept_name`, `order_num`, `leader`, `phone`, `email`, `status`, `del_flag`, `create_by`, `create_time`, `update_by`, `update_time`) VALUES (100,0,'0','工程中心',0,'朱涵威','','','0','0','admin','2025-10-16 10:32:52','admin','2025-10-16 14:41:37'),(101,100,'0,100','开发施工',1,'','','','0','0','admin','2025-10-16 10:32:52','admin','2025-10-17 09:22:10'),(102,100,'0,100','设计装饰',2,'','','','0','0','admin','2025-10-16 10:32:52','admin','2025-10-17 09:22:20'),(103,100,'0,100','系统管理账号',100,'','','','0','0','admin','2025-10-16 10:32:52','admin','2025-10-17 09:23:15'),(104,101,'0,100,101','市场部门',2,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(105,101,'0,100,101','测试部门',3,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(106,101,'0,100,101','财务部门',4,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(107,101,'0,100,101','运维部门',5,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(108,102,'0,100,102','市场部门',1,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(109,102,'0,100,102','财务部门',2,'年糕','15888888888','niangao@qq.com','0','2','admin','2025-10-16 10:32:52',NULL,NULL),(200,100,'0,100','财务合约',3,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:22:35','admin','2025-10-17 09:22:35'),(201,101,'0,100,101','土建管理1',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:23:39','admin','2025-10-17 09:23:39'),(202,101,'0,100,101','土建管理2',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:23:46','admin','2025-10-17 09:23:46'),(203,101,'0,100,101','土建管理3',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:23:50','admin','2025-10-17 09:23:50'),(204,102,'0,100,102','公装管理1',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:24:21','admin','2025-10-17 09:25:05'),(205,102,'0,100,102','公装管理2',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:24:29','admin','2025-10-17 09:25:10'),(206,102,'0,100,102','店装管理1',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:24:44','admin','2025-10-17 09:24:44'),(207,102,'0,100,102','店装管理2',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:24:48','admin','2025-10-17 09:24:48'),(208,102,'0,100,102','店装管理3',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:24:51','admin','2025-10-17 09:24:51'),(209,102,'0,100,102','建筑设计',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:25:38','admin','2025-10-17 09:25:38'),(210,200,'0,100,200','人事财务',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:25:56','admin','2025-10-17 09:25:56'),(211,200,'0,100,200','成本合约',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:26:03','admin','2025-10-17 09:26:03'),(212,200,'0,100,200','行政财务',0,NULL,NULL,NULL,'0','0','admin','2025-10-17 09:26:09','admin','2025-10-17 09:26:09');
/*!40000 ALTER TABLE `sys_dept` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dict_data`
--

LOCK TABLES `sys_dict_data` WRITE;
/*!40000 ALTER TABLE `sys_dict_data` DISABLE KEYS */;
INSERT INTO `sys_dict_data` (`dict_code`, `dict_sort`, `dict_label`, `dict_value`, `dict_type`, `css_class`, `list_class`, `is_default`, `status`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,1,'男','0','sys_user_sex','','','Y','0','admin','2025-10-16 10:32:52','',NULL,'性别男'),(2,2,'女','1','sys_user_sex','','','N','0','admin','2025-10-16 10:32:52','',NULL,'性别女'),(3,3,'未知','2','sys_user_sex','','','N','0','admin','2025-10-16 10:32:52','',NULL,'性别未知'),(4,1,'显示','0','sys_show_hide','','primary','Y','0','admin','2025-10-16 10:32:52','',NULL,'显示菜单'),(5,2,'隐藏','1','sys_show_hide','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'隐藏菜单'),(6,1,'正常','0','sys_normal_disable','','primary','Y','0','admin','2025-10-16 10:32:52','',NULL,'正常状态'),(7,2,'停用','1','sys_normal_disable','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'停用状态'),(8,1,'正常','0','sys_job_status','','primary','Y','0','admin','2025-10-16 10:32:52','',NULL,'正常状态'),(9,2,'暂停','1','sys_job_status','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'停用状态'),(10,1,'默认','default','sys_job_group','','','Y','0','admin','2025-10-16 10:32:52','',NULL,'默认分组'),(11,2,'数据库','sqlalchemy','sys_job_group','','','N','0','admin','2025-10-16 10:32:52','',NULL,'数据库分组'),(12,3,'redis','redis','sys_job_group','','','N','0','admin','2025-10-16 10:32:52','',NULL,'reids分组'),(13,1,'默认','default','sys_job_executor','','','N','0','admin','2025-10-16 10:32:52','',NULL,'线程池'),(14,2,'进程池','processpool','sys_job_executor','','','N','0','admin','2025-10-16 10:32:52','',NULL,'进程池'),(15,1,'是','Y','sys_yes_no','','primary','Y','0','admin','2025-10-16 10:32:52','',NULL,'系统默认是'),(16,2,'否','N','sys_yes_no','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'系统默认否'),(17,1,'通知','1','sys_notice_type','','warning','Y','0','admin','2025-10-16 10:32:52','',NULL,'通知'),(18,2,'公告','2','sys_notice_type','','success','N','0','admin','2025-10-16 10:32:52','',NULL,'公告'),(19,1,'正常','0','sys_notice_status','','primary','Y','0','admin','2025-10-16 10:32:52','',NULL,'正常状态'),(20,2,'关闭','1','sys_notice_status','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'关闭状态'),(21,99,'其他','0','sys_oper_type','','info','N','0','admin','2025-10-16 10:32:52','',NULL,'其他操作'),(22,1,'新增','1','sys_oper_type','','info','N','0','admin','2025-10-16 10:32:52','',NULL,'新增操作'),(23,2,'修改','2','sys_oper_type','','info','N','0','admin','2025-10-16 10:32:52','',NULL,'修改操作'),(24,3,'删除','3','sys_oper_type','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'删除操作'),(25,4,'授权','4','sys_oper_type','','primary','N','0','admin','2025-10-16 10:32:52','',NULL,'授权操作'),(26,5,'导出','5','sys_oper_type','','warning','N','0','admin','2025-10-16 10:32:52','',NULL,'导出操作'),(27,6,'导入','6','sys_oper_type','','warning','N','0','admin','2025-10-16 10:32:52','',NULL,'导入操作'),(28,7,'强退','7','sys_oper_type','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'强退操作'),(29,8,'生成代码','8','sys_oper_type','','warning','N','0','admin','2025-10-16 10:32:52','',NULL,'生成操作'),(30,9,'清空数据','9','sys_oper_type','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'清空操作'),(31,1,'成功','0','sys_common_status','','primary','N','0','admin','2025-10-16 10:32:52','',NULL,'正常状态'),(32,2,'失败','1','sys_common_status','','danger','N','0','admin','2025-10-16 10:32:52','',NULL,'停用状态');
/*!40000 ALTER TABLE `sys_dict_data` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典类型表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dict_type`
--

LOCK TABLES `sys_dict_type` WRITE;
/*!40000 ALTER TABLE `sys_dict_type` DISABLE KEYS */;
INSERT INTO `sys_dict_type` (`dict_id`, `dict_name`, `dict_type`, `status`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'用户性别','sys_user_sex','0','admin','2025-10-16 10:32:52','',NULL,'用户性别列表'),(2,'菜单状态','sys_show_hide','0','admin','2025-10-16 10:32:52','',NULL,'菜单状态列表'),(3,'系统开关','sys_normal_disable','0','admin','2025-10-16 10:32:52','',NULL,'系统开关列表'),(4,'任务状态','sys_job_status','0','admin','2025-10-16 10:32:52','',NULL,'任务状态列表'),(5,'任务分组','sys_job_group','0','admin','2025-10-16 10:32:52','',NULL,'任务分组列表'),(6,'任务执行器','sys_job_executor','0','admin','2025-10-16 10:32:52','',NULL,'任务执行器列表'),(7,'系统是否','sys_yes_no','0','admin','2025-10-16 10:32:52','',NULL,'系统是否列表'),(8,'通知类型','sys_notice_type','0','admin','2025-10-16 10:32:52','',NULL,'通知类型列表'),(9,'通知状态','sys_notice_status','0','admin','2025-10-16 10:32:52','',NULL,'通知状态列表'),(10,'操作类型','sys_oper_type','0','admin','2025-10-16 10:32:52','',NULL,'操作类型列表'),(11,'系统状态','sys_common_status','0','admin','2025-10-16 10:32:52','',NULL,'登录状态列表');
/*!40000 ALTER TABLE `sys_dict_type` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='定时任务调度表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_job`
--

LOCK TABLES `sys_job` WRITE;
/*!40000 ALTER TABLE `sys_job` DISABLE KEYS */;
INSERT INTO `sys_job` (`job_id`, `job_name`, `job_group`, `job_executor`, `invoke_target`, `job_args`, `job_kwargs`, `cron_expression`, `misfire_policy`, `concurrent`, `status`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'系统默认（无参）','default','default','module_task.scheduler_test.job',NULL,NULL,'0/10 * * * * ?','3','1','1','admin','2025-10-16 10:32:52','',NULL,''),(2,'系统默认（有参）','default','default','module_task.scheduler_test.job','test',NULL,'0/15 * * * * ?','3','1','1','admin','2025-10-16 10:32:52','',NULL,''),(3,'系统默认（多参）','default','default','module_task.scheduler_test.job','new','{\"test\": 111}','0/20 * * * * ?','3','1','1','admin','2025-10-16 10:32:52','',NULL,'');
/*!40000 ALTER TABLE `sys_job` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sys_job_log`
--

LOCK TABLES `sys_job_log` WRITE;
/*!40000 ALTER TABLE `sys_job_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_job_log` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统访问记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_logininfor`
--

LOCK TABLES `sys_logininfor` WRITE;
/*!40000 ALTER TABLE `sys_logininfor` DISABLE KEYS */;
INSERT INTO `sys_logininfor` (`info_id`, `user_name`, `ipaddr`, `login_location`, `browser`, `os`, `status`, `msg`, `login_time`) VALUES (100,'admin','','未知','Chrome 141','Mac OS X 10','0','登录成功','2025-10-16 11:15:58'),(101,'admin','','未知','Chrome 141','Mac OS X 10','0','登录成功','2025-10-16 14:31:42'),(102,'admin','','未知','Chrome 141','Mac OS X 10','1','验证码已失效','2025-10-16 16:15:36'),(103,'admin','','未知','Chrome 141','Mac OS X 10','0','登录成功','2025-10-16 16:15:42'),(104,'admin','','未知','Chrome 141','Mac OS X 10','0','登录成功','2025-10-17 09:21:11'),(105,'admin','','未知','Chrome 141','Mac OS X 10','0','登录成功','2025-10-17 12:22:19');
/*!40000 ALTER TABLE `sys_logininfor` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=2006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='菜单权限表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_menu`
--

LOCK TABLES `sys_menu` WRITE;
/*!40000 ALTER TABLE `sys_menu` DISABLE KEYS */;
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `query`, `route_name`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'系统管理',0,1,'system',NULL,'','',1,0,'M','0','0','','system','admin','2025-10-16 10:32:52','',NULL,'系统管理目录'),(2,'系统监控',0,2,'monitor',NULL,'','',1,0,'M','0','0','','monitor','admin','2025-10-16 10:32:52','',NULL,'系统监控目录'),(3,'系统工具',0,3,'tool',NULL,'','',1,0,'M','0','0','','tool','admin','2025-10-16 10:32:52','',NULL,'系统工具目录'),(4,'若依官网',0,4,'http://ruoyi.vip',NULL,'','',0,0,'M','0','0','','guide','admin','2025-10-16 10:32:52','',NULL,'若依官网地址'),(100,'用户管理',1,1,'user','system/user/index','','',1,0,'C','0','0','system:user:list','user','admin','2025-10-16 10:32:52','',NULL,'用户管理菜单'),(101,'角色管理',1,2,'role','system/role/index','','',1,0,'C','0','0','system:role:list','peoples','admin','2025-10-16 10:32:52','',NULL,'角色管理菜单'),(102,'菜单管理',1,3,'menu','system/menu/index','','',1,0,'C','0','0','system:menu:list','tree-table','admin','2025-10-16 10:32:52','',NULL,'菜单管理菜单'),(103,'部门管理',1,4,'dept','system/dept/index','','',1,0,'C','0','0','system:dept:list','tree','admin','2025-10-16 10:32:52','',NULL,'部门管理菜单'),(104,'岗位管理',1,5,'post','system/post/index','','',1,0,'C','0','0','system:post:list','post','admin','2025-10-16 10:32:52','',NULL,'岗位管理菜单'),(105,'字典管理',1,6,'dict','system/dict/index','','',1,0,'C','0','0','system:dict:list','dict','admin','2025-10-16 10:32:52','',NULL,'字典管理菜单'),(106,'参数设置',1,7,'config','system/config/index','','',1,0,'C','0','0','system:config:list','edit','admin','2025-10-16 10:32:52','',NULL,'参数设置菜单'),(107,'通知公告',1,8,'notice','system/notice/index','','',1,0,'C','0','0','system:notice:list','message','admin','2025-10-16 10:32:52','',NULL,'通知公告菜单'),(108,'日志管理',1,9,'log','','','',1,0,'M','0','0','','log','admin','2025-10-16 10:32:52','',NULL,'日志管理菜单'),(109,'在线用户',2,1,'online','monitor/online/index','','',1,0,'C','0','0','monitor:online:list','online','admin','2025-10-16 10:32:52','',NULL,'在线用户菜单'),(110,'定时任务',2,2,'job','monitor/job/index','','',1,0,'C','0','0','monitor:job:list','job','admin','2025-10-16 10:32:52','',NULL,'定时任务菜单'),(111,'数据监控',2,3,'druid','monitor/druid/index','','',1,0,'C','0','0','monitor:druid:list','druid','admin','2025-10-16 10:32:52','',NULL,'数据监控菜单'),(112,'服务监控',2,4,'server','monitor/server/index','','',1,0,'C','0','0','monitor:server:list','server','admin','2025-10-16 10:32:52','',NULL,'服务监控菜单'),(113,'缓存监控',2,5,'cache','monitor/cache/index','','',1,0,'C','0','0','monitor:cache:list','redis','admin','2025-10-16 10:32:52','',NULL,'缓存监控菜单'),(114,'缓存列表',2,6,'cacheList','monitor/cache/list','','',1,0,'C','0','0','monitor:cache:list','redis-list','admin','2025-10-16 10:32:52','',NULL,'缓存列表菜单'),(115,'表单构建',3,1,'build','tool/build/index','','',1,0,'C','0','0','tool:build:list','build','admin','2025-10-16 10:32:52','',NULL,'表单构建菜单'),(116,'代码生成',3,2,'gen','tool/gen/index','','',1,0,'C','0','0','tool:gen:list','code','admin','2025-10-16 10:32:52','',NULL,'代码生成菜单'),(117,'系统接口',3,3,'swagger','tool/swagger/index','','',1,0,'C','0','0','tool:swagger:list','swagger','admin','2025-10-16 10:32:52','',NULL,'系统接口菜单'),(500,'操作日志',108,1,'operlog','monitor/operlog/index','','',1,0,'C','0','0','monitor:operlog:list','form','admin','2025-10-16 10:32:52','',NULL,'操作日志菜单'),(501,'登录日志',108,2,'logininfor','monitor/logininfor/index','','',1,0,'C','0','0','monitor:logininfor:list','logininfor','admin','2025-10-16 10:32:52','',NULL,'登录日志菜单'),(1000,'用户查询',100,1,'','','','',1,0,'F','0','0','system:user:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1001,'用户新增',100,2,'','','','',1,0,'F','0','0','system:user:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1002,'用户修改',100,3,'','','','',1,0,'F','0','0','system:user:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1003,'用户删除',100,4,'','','','',1,0,'F','0','0','system:user:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1004,'用户导出',100,5,'','','','',1,0,'F','0','0','system:user:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1005,'用户导入',100,6,'','','','',1,0,'F','0','0','system:user:import','#','admin','2025-10-16 10:32:52','',NULL,''),(1006,'重置密码',100,7,'','','','',1,0,'F','0','0','system:user:resetPwd','#','admin','2025-10-16 10:32:52','',NULL,''),(1007,'角色查询',101,1,'','','','',1,0,'F','0','0','system:role:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1008,'角色新增',101,2,'','','','',1,0,'F','0','0','system:role:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1009,'角色修改',101,3,'','','','',1,0,'F','0','0','system:role:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1010,'角色删除',101,4,'','','','',1,0,'F','0','0','system:role:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1011,'角色导出',101,5,'','','','',1,0,'F','0','0','system:role:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1012,'菜单查询',102,1,'','','','',1,0,'F','0','0','system:menu:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1013,'菜单新增',102,2,'','','','',1,0,'F','0','0','system:menu:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1014,'菜单修改',102,3,'','','','',1,0,'F','0','0','system:menu:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1015,'菜单删除',102,4,'','','','',1,0,'F','0','0','system:menu:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1016,'部门查询',103,1,'','','','',1,0,'F','0','0','system:dept:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1017,'部门新增',103,2,'','','','',1,0,'F','0','0','system:dept:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1018,'部门修改',103,3,'','','','',1,0,'F','0','0','system:dept:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1019,'部门删除',103,4,'','','','',1,0,'F','0','0','system:dept:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1020,'岗位查询',104,1,'','','','',1,0,'F','0','0','system:post:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1021,'岗位新增',104,2,'','','','',1,0,'F','0','0','system:post:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1022,'岗位修改',104,3,'','','','',1,0,'F','0','0','system:post:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1023,'岗位删除',104,4,'','','','',1,0,'F','0','0','system:post:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1024,'岗位导出',104,5,'','','','',1,0,'F','0','0','system:post:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1025,'字典查询',105,1,'#','','','',1,0,'F','0','0','system:dict:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1026,'字典新增',105,2,'#','','','',1,0,'F','0','0','system:dict:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1027,'字典修改',105,3,'#','','','',1,0,'F','0','0','system:dict:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1028,'字典删除',105,4,'#','','','',1,0,'F','0','0','system:dict:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1029,'字典导出',105,5,'#','','','',1,0,'F','0','0','system:dict:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1030,'参数查询',106,1,'#','','','',1,0,'F','0','0','system:config:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1031,'参数新增',106,2,'#','','','',1,0,'F','0','0','system:config:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1032,'参数修改',106,3,'#','','','',1,0,'F','0','0','system:config:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1033,'参数删除',106,4,'#','','','',1,0,'F','0','0','system:config:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1034,'参数导出',106,5,'#','','','',1,0,'F','0','0','system:config:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1035,'公告查询',107,1,'#','','','',1,0,'F','0','0','system:notice:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1036,'公告新增',107,2,'#','','','',1,0,'F','0','0','system:notice:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1037,'公告修改',107,3,'#','','','',1,0,'F','0','0','system:notice:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1038,'公告删除',107,4,'#','','','',1,0,'F','0','0','system:notice:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1039,'操作查询',500,1,'#','','','',1,0,'F','0','0','monitor:operlog:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1040,'操作删除',500,2,'#','','','',1,0,'F','0','0','monitor:operlog:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1041,'日志导出',500,3,'#','','','',1,0,'F','0','0','monitor:operlog:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1042,'登录查询',501,1,'#','','','',1,0,'F','0','0','monitor:logininfor:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1043,'登录删除',501,2,'#','','','',1,0,'F','0','0','monitor:logininfor:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1044,'日志导出',501,3,'#','','','',1,0,'F','0','0','monitor:logininfor:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1045,'账户解锁',501,4,'#','','','',1,0,'F','0','0','monitor:logininfor:unlock','#','admin','2025-10-16 10:32:52','',NULL,''),(1046,'在线查询',109,1,'#','','','',1,0,'F','0','0','monitor:online:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1047,'批量强退',109,2,'#','','','',1,0,'F','0','0','monitor:online:batchLogout','#','admin','2025-10-16 10:32:52','',NULL,''),(1048,'单条强退',109,3,'#','','','',1,0,'F','0','0','monitor:online:forceLogout','#','admin','2025-10-16 10:32:52','',NULL,''),(1049,'任务查询',110,1,'#','','','',1,0,'F','0','0','monitor:job:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1050,'任务新增',110,2,'#','','','',1,0,'F','0','0','monitor:job:add','#','admin','2025-10-16 10:32:52','',NULL,''),(1051,'任务修改',110,3,'#','','','',1,0,'F','0','0','monitor:job:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1052,'任务删除',110,4,'#','','','',1,0,'F','0','0','monitor:job:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1053,'状态修改',110,5,'#','','','',1,0,'F','0','0','monitor:job:changeStatus','#','admin','2025-10-16 10:32:52','',NULL,''),(1054,'任务导出',110,6,'#','','','',1,0,'F','0','0','monitor:job:export','#','admin','2025-10-16 10:32:52','',NULL,''),(1055,'生成查询',116,1,'#','','','',1,0,'F','0','0','tool:gen:query','#','admin','2025-10-16 10:32:52','',NULL,''),(1056,'生成修改',116,2,'#','','','',1,0,'F','0','0','tool:gen:edit','#','admin','2025-10-16 10:32:52','',NULL,''),(1057,'生成删除',116,3,'#','','','',1,0,'F','0','0','tool:gen:remove','#','admin','2025-10-16 10:32:52','',NULL,''),(1058,'导入代码',116,4,'#','','','',1,0,'F','0','0','tool:gen:import','#','admin','2025-10-16 10:32:52','',NULL,''),(1059,'预览代码',116,5,'#','','','',1,0,'F','0','0','tool:gen:preview','#','admin','2025-10-16 10:32:52','',NULL,''),(1060,'生成代码',116,6,'#','','','',1,0,'F','0','0','tool:gen:code','#','admin','2025-10-16 10:32:52','',NULL,''),(2000,'工作台',0,0,'workbench','workbench/index',NULL,'',1,0,'C','0','0',NULL,'number','admin','2025-10-17 09:27:37','admin','2025-10-17 09:35:09',''),(2001,'日常工作',2000,1,'123',NULL,NULL,'',1,0,'M','0','0',NULL,'404','admin','2025-10-17 10:10:14','admin','2025-10-17 10:15:54',''),(2002,'项目推进',2001,1,'1',NULL,NULL,'',1,0,'C','0','0',NULL,'404','admin','2025-10-17 10:14:58','admin','2025-10-17 10:14:58',''),(2003,'资产管理',2000,2,'1',NULL,NULL,'',1,0,'M','0','0',NULL,'#','admin','2025-10-17 10:15:36','admin','2025-10-17 10:15:36',''),(2004,'文件管理',2003,1,'1',NULL,NULL,'',1,0,'C','0','0',NULL,'documentation','admin','2025-10-17 10:16:16','admin','2025-10-17 10:16:16',''),(2005,'周期任务配置',2001,2,'1',NULL,NULL,'',1,0,'C','0','0',NULL,'dict','admin','2025-10-17 10:16:56','admin','2025-10-17 10:17:12','');
/*!40000 ALTER TABLE `sys_menu` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='通知公告表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_notice`
--

LOCK TABLES `sys_notice` WRITE;
/*!40000 ALTER TABLE `sys_notice` DISABLE KEYS */;
INSERT INTO `sys_notice` (`notice_id`, `notice_title`, `notice_type`, `notice_content`, `status`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'温馨提醒：2018-07-01 vfadmin新版本发布啦','2',0xE696B0E78988E69CACE58685E5AEB9,'0','admin','2025-10-16 10:32:52','',NULL,'管理员'),(2,'维护通知：2018-07-01 vfadmin系统凌晨维护','1',0xE7BBB4E68AA4E58685E5AEB9,'0','admin','2025-10-16 10:32:52','',NULL,'管理员');
/*!40000 ALTER TABLE `sys_notice` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='操作日志记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_oper_log`
--

LOCK TABLES `sys_oper_log` WRITE;
/*!40000 ALTER TABLE `sys_oper_log` DISABLE KEYS */;
INSERT INTO `sys_oper_log` (`oper_id`, `title`, `business_type`, `method`, `request_method`, `operator_type`, `oper_name`, `dept_name`, `oper_url`, `oper_ip`, `oper_location`, `oper_param`, `json_result`, `status`, `error_msg`, `oper_time`, `cost_time`) VALUES (100,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','研发部门','/dev-api/system/dept','','未知','{\"deptId\": 100, \"parentId\": 0, \"ancestors\": \"0\", \"deptName\": \"工程中心\", \"orderNum\": 0, \"leader\": \"朱涵威\", \"phone\": \"\", \"email\": \"\", \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:41:37.089835\"}',0,'','2025-10-16 14:41:37',11),(101,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/101','','未知','{\"dept_ids\": \"101\"}','{\"code\": 601, \"msg\": \"存在下级部门,不允许删除\", \"success\": false, \"time\": \"2025-10-16T14:41:53.218063\"}',1,'存在下级部门,不允许删除','2025-10-16 14:41:53',2),(102,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/103','','未知','{\"dept_ids\": \"103\"}','{\"code\": 601, \"msg\": \"部门存在用户,不允许删除\", \"success\": false, \"time\": \"2025-10-16T14:41:58.281142\"}',1,'部门存在用户,不允许删除','2025-10-16 14:41:58',3),(103,'用户管理',3,'module_admin.controller.user_controller.delete_system_user()','DELETE',1,'admin','研发部门','/dev-api/system/user/2','','未知','{\"user_ids\": \"2\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-16T14:42:39.053624\"}',0,'','2025-10-16 14:42:39',21),(104,'用户管理',1,'module_admin.controller.user_controller.add_system_user()','POST',1,'admin','研发部门','/dev-api/system/user','','未知','{\"deptId\": 100, \"userName\": \"朱涵威\", \"nickName\": \"朱涵威\", \"password\": \"123456\", \"status\": \"0\", \"postIds\": [], \"roleIds\": []}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-16T14:43:06.879009\"}',0,'','2025-10-16 14:43:07',235),(105,'岗位管理',2,'module_admin.controller.post_controler.edit_system_post()','PUT',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postId\": 1, \"postCode\": \"P8\", \"postName\": \"总裁\", \"postSort\": 1, \"status\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null, \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:55:18.599941\"}',0,'','2025-10-16 14:55:19',7),(106,'岗位管理',2,'module_admin.controller.post_controler.edit_system_post()','PUT',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postId\": 2, \"postCode\": \"P7\", \"postName\": \"总经理\", \"postSort\": 2, \"status\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null, \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:55:31.912847\"}',0,'','2025-10-16 14:55:32',11),(107,'岗位管理',2,'module_admin.controller.post_controler.edit_system_post()','PUT',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postId\": 3, \"postCode\": \"P6\", \"postName\": \"总监\", \"postSort\": 3, \"status\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null, \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:55:42.250943\"}',0,'','2025-10-16 14:55:42',9),(108,'岗位管理',2,'module_admin.controller.post_controler.edit_system_post()','PUT',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postId\": 4, \"postCode\": \"P5\", \"postName\": \"经理\", \"postSort\": 4, \"status\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null, \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:55:53.991285\"}',0,'','2025-10-16 14:55:54',6),(109,'岗位管理',1,'module_admin.controller.post_controler.add_system_post()','POST',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postCode\": \"P4\", \"postName\": \"总管\", \"postSort\": 5, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-16T14:56:05.875110\"}',0,'','2025-10-16 14:56:06',12),(110,'岗位管理',1,'module_admin.controller.post_controler.add_system_post()','POST',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postCode\": \"主管\", \"postName\": \"P3\", \"postSort\": 6, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-16T14:56:20.642222\"}',0,'','2025-10-16 14:56:21',10),(111,'岗位管理',1,'module_admin.controller.post_controler.add_system_post()','POST',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postCode\": \"P2\", \"postName\": \"组长\", \"postSort\": 7, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-16T14:56:32.943640\"}',0,'','2025-10-16 14:56:33',11),(112,'岗位管理',2,'module_admin.controller.post_controler.edit_system_post()','PUT',1,'admin','研发部门','/dev-api/system/post','','未知','{\"postId\": 6, \"postCode\": \"P3\", \"postName\": \"主管\", \"postSort\": 6, \"status\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T14:56:21\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-16T14:56:21\", \"remark\": null}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-16T14:56:38.546501\"}',0,'','2025-10-16 14:56:39',11),(113,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','研发部门','/dev-api/system/dept','','未知','{\"deptId\": 101, \"parentId\": 100, \"ancestors\": \"0,100\", \"deptName\": \"开发施工\", \"orderNum\": 1, \"leader\": \"\", \"phone\": \"\", \"email\": \"\", \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:22:09.976378\"}',0,'','2025-10-17 09:22:10',24),(114,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','研发部门','/dev-api/system/dept','','未知','{\"deptId\": 102, \"parentId\": 100, \"ancestors\": \"0,100\", \"deptName\": \"设计装饰\", \"orderNum\": 2, \"leader\": \"\", \"phone\": \"\", \"email\": \"\", \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:22:19.783262\"}',0,'','2025-10-17 09:22:20',14),(115,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','研发部门','/dev-api/system/dept','','未知','{\"parentId\": 100, \"deptName\": \"财务合约\", \"orderNum\": 3, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:22:35.472296\"}',0,'','2025-10-17 09:22:35',13),(116,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/108','','未知','{\"dept_ids\": \"108\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:39.016056\"}',0,'','2025-10-17 09:22:39',12),(117,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/109','','未知','{\"dept_ids\": \"109\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:40.793765\"}',0,'','2025-10-17 09:22:41',8),(118,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/107','','未知','{\"dept_ids\": \"107\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:42.871947\"}',0,'','2025-10-17 09:22:43',7),(119,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/106','','未知','{\"dept_ids\": \"106\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:45.578634\"}',0,'','2025-10-17 09:22:46',10),(120,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/105','','未知','{\"dept_ids\": \"105\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:47.260310\"}',0,'','2025-10-17 09:22:47',10),(121,'部门管理',3,'module_admin.controller.dept_controller.delete_system_dept()','DELETE',1,'admin','研发部门','/dev-api/system/dept/104','','未知','{\"dept_ids\": \"104\"}','{\"code\": 200, \"msg\": \"删除成功\", \"success\": true, \"time\": \"2025-10-17T09:22:49.734983\"}',0,'','2025-10-17 09:22:50',5),(122,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','研发部门','/dev-api/system/dept','','未知','{\"deptId\": 103, \"parentId\": 100, \"ancestors\": \"0,100,101\", \"deptName\": \"研发部门\", \"orderNum\": 1, \"leader\": \"年糕\", \"phone\": \"15888888888\", \"email\": \"niangao@qq.com\", \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"\", \"updateTime\": null}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:22:56.280819\"}',0,'','2025-10-17 09:22:56',11),(123,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"deptId\": 103, \"parentId\": 100, \"ancestors\": \"0,100\", \"deptName\": \"系统管理账号\", \"orderNum\": 100, \"leader\": \"\", \"phone\": \"\", \"email\": \"\", \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-16T10:32:52\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:22:56\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:23:15.503875\"}',0,'','2025-10-17 09:23:15',14),(124,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 101, \"deptName\": \"土建管理1\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:23:38.787382\"}',0,'','2025-10-17 09:23:39',11),(125,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 101, \"deptName\": \"土建管理2\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:23:45.699501\"}',0,'','2025-10-17 09:23:46',10),(126,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 101, \"deptName\": \"土建管理3\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:23:49.884544\"}',0,'','2025-10-17 09:23:50',8),(127,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"工装管理1\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:24:21.117911\"}',0,'','2025-10-17 09:24:21',10),(128,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"工装管理2\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:24:29.017969\"}',0,'','2025-10-17 09:24:29',9),(129,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"店装管理1\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:24:44.198002\"}',0,'','2025-10-17 09:24:44',106),(130,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"店装管理2\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:24:47.941710\"}',0,'','2025-10-17 09:24:48',10),(131,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"店装管理3\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:24:50.871467\"}',0,'','2025-10-17 09:24:51',10),(132,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"deptId\": 204, \"parentId\": 102, \"ancestors\": \"0,100,102\", \"deptName\": \"公装管理1\", \"orderNum\": 0, \"leader\": null, \"phone\": null, \"email\": null, \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:24:21\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:24:21\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:25:05.442481\"}',0,'','2025-10-17 09:25:05',14),(133,'部门管理',2,'module_admin.controller.dept_controller.edit_system_dept()','PUT',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"deptId\": 205, \"parentId\": 102, \"ancestors\": \"0,100,102\", \"deptName\": \"公装管理2\", \"orderNum\": 0, \"leader\": null, \"phone\": null, \"email\": null, \"status\": \"0\", \"delFlag\": \"0\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:24:29\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:24:29\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:25:10.011279\"}',0,'','2025-10-17 09:25:10',14),(134,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 102, \"deptName\": \"建筑设计\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:25:37.613099\"}',0,'','2025-10-17 09:25:38',11),(135,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 200, \"deptName\": \"人事财务\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:25:55.801941\"}',0,'','2025-10-17 09:25:56',12),(136,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 200, \"deptName\": \"成本合约\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:26:02.939411\"}',0,'','2025-10-17 09:26:03',10),(137,'部门管理',1,'module_admin.controller.dept_controller.add_system_dept()','POST',1,'admin','系统管理账号','/dev-api/system/dept','','未知','{\"parentId\": 200, \"deptName\": \"行政财务\", \"orderNum\": 0, \"status\": \"0\"}','{\"code\": 200, \"msg\": \"操作成功\", \"data\": {\"is_success\": true, \"message\": \"新增成功\", \"result\": null}, \"success\": true, \"time\": \"2025-10-17T09:26:08.705964\"}',0,'','2025-10-17 09:26:09',12),(138,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 0, \"menuName\": \"任务配置\", \"icon\": \"number\", \"menuType\": \"M\", \"orderNum\": 0, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"123\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T09:27:36.943746\"}',0,'','2025-10-17 09:27:37',12),(139,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2000, \"menuName\": \"工作台\", \"parentId\": 0, \"orderNum\": 0, \"path\": \"workbench\", \"component\": null, \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"M\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"number\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:27:37\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:27:37\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:32:17.516396\"}',0,'','2025-10-17 09:32:17',20),(140,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2000, \"menuName\": \"工作台\", \"parentId\": 0, \"orderNum\": 0, \"path\": \"workbench/index\", \"component\": null, \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"M\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"number\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:27:37\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:32:17\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:33:23.502910\"}',0,'','2025-10-17 09:33:23',33),(141,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2000, \"menuName\": \"工作台\", \"parentId\": 0, \"orderNum\": 0, \"path\": \"workbench\", \"component\": \"index.vue\", \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"C\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"number\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:27:37\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:33:23\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:34:19.290790\"}',0,'','2025-10-17 09:34:19',21),(142,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2000, \"menuName\": \"工作台\", \"parentId\": 0, \"orderNum\": 0, \"path\": \"workbench\", \"component\": \"workbench/index\", \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"C\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"number\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T09:27:37\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T09:34:19\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T09:35:08.877443\"}',0,'','2025-10-17 09:35:09',11),(143,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 2000, \"menuName\": \"123\", \"icon\": \"404\", \"menuType\": \"M\", \"orderNum\": 0, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"123\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T10:10:13.887033\"}',0,'','2025-10-17 10:10:14',10),(144,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2001, \"menuName\": \"日常工作\", \"parentId\": 2000, \"orderNum\": 0, \"path\": \"123\", \"component\": null, \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"M\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"404\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T10:10:14\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T10:10:14\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T10:14:35.896126\"}',0,'','2025-10-17 10:14:36',15),(145,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 2001, \"menuName\": \"项目推进\", \"icon\": \"404\", \"menuType\": \"C\", \"orderNum\": 1, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"1\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T10:14:58.492871\"}',0,'','2025-10-17 10:14:58',10),(146,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 2000, \"menuName\": \"资产管理\", \"menuType\": \"M\", \"orderNum\": 2, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"1\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T10:15:35.748276\"}',0,'','2025-10-17 10:15:36',13),(147,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2001, \"menuName\": \"日常工作\", \"parentId\": 2000, \"orderNum\": 1, \"path\": \"123\", \"component\": null, \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"M\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"404\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T10:10:14\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T10:14:36\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T10:15:54.106890\"}',0,'','2025-10-17 10:15:54',9),(148,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 2003, \"menuName\": \"文件管理\", \"icon\": \"documentation\", \"menuType\": \"C\", \"orderNum\": 1, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"1\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T10:16:16.324280\"}',0,'','2025-10-17 10:16:16',16),(149,'菜单管理',1,'module_admin.controller.menu_controller.add_system_menu()','POST',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"parentId\": 2002, \"menuName\": \"周期任务配置\", \"icon\": \"dict\", \"menuType\": \"C\", \"orderNum\": 2, \"isFrame\": 1, \"isCache\": 0, \"visible\": \"0\", \"status\": \"0\", \"path\": \"1\"}','{\"code\": 200, \"msg\": \"新增成功\", \"success\": true, \"time\": \"2025-10-17T10:16:55.843728\"}',0,'','2025-10-17 10:16:56',9),(150,'菜单管理',2,'module_admin.controller.menu_controller.edit_system_menu()','PUT',1,'admin','系统管理账号','/dev-api/system/menu','','未知','{\"menuId\": 2005, \"menuName\": \"周期任务配置\", \"parentId\": 2001, \"orderNum\": 2, \"path\": \"1\", \"component\": null, \"query\": null, \"routeName\": \"\", \"isFrame\": 1, \"isCache\": 0, \"menuType\": \"C\", \"visible\": \"0\", \"status\": \"0\", \"perms\": null, \"icon\": \"dict\", \"createBy\": \"admin\", \"createTime\": \"2025-10-17T10:16:56\", \"updateBy\": \"admin\", \"updateTime\": \"2025-10-17T10:16:56\", \"remark\": \"\"}','{\"code\": 200, \"msg\": \"更新成功\", \"success\": true, \"time\": \"2025-10-17T10:17:11.530653\"}',0,'','2025-10-17 10:17:12',13);
/*!40000 ALTER TABLE `sys_oper_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_post`
--

DROP TABLE IF EXISTS `sys_post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_post` (
  `post_id` bigint NOT NULL AUTO_INCREMENT COMMENT '岗位ID',
  `post_code` varchar(64) NOT NULL COMMENT '岗位编码',
  `post_name` varchar(50) NOT NULL COMMENT '岗位名称',
  `post_sort` int NOT NULL COMMENT '显示顺序',
  `status` char(1) NOT NULL COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`post_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='岗位信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_post`
--

LOCK TABLES `sys_post` WRITE;
/*!40000 ALTER TABLE `sys_post` DISABLE KEYS */;
INSERT INTO `sys_post` (`post_id`, `post_code`, `post_name`, `post_sort`, `status`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'P8','总裁',1,'0','admin','2025-10-16 10:32:52','admin','2025-10-16 14:55:19',''),(2,'P7','总经理',2,'0','admin','2025-10-16 10:32:52','admin','2025-10-16 14:55:32',''),(3,'P6','总监',3,'0','admin','2025-10-16 10:32:52','admin','2025-10-16 14:55:42',''),(4,'P5','经理',4,'0','admin','2025-10-16 10:32:52','admin','2025-10-16 14:55:54',''),(5,'P4','总管',5,'0','admin','2025-10-16 14:56:06','admin','2025-10-16 14:56:06',NULL),(6,'P3','主管',6,'0','admin','2025-10-16 14:56:21','admin','2025-10-16 14:56:39',NULL),(7,'P2','组长',7,'0','admin','2025-10-16 14:56:33','admin','2025-10-16 14:56:33',NULL);
/*!40000 ALTER TABLE `sys_post` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_role`
--

LOCK TABLES `sys_role` WRITE;
/*!40000 ALTER TABLE `sys_role` DISABLE KEYS */;
INSERT INTO `sys_role` (`role_id`, `role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `del_flag`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,'超级管理员','admin',1,'1',1,1,'0','0','admin','2025-10-16 10:32:52','',NULL,'超级管理员'),(2,'普通角色','common',2,'2',1,1,'0','0','admin','2025-10-16 10:32:52','',NULL,'普通角色');
/*!40000 ALTER TABLE `sys_role` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sys_role_dept`
--

LOCK TABLES `sys_role_dept` WRITE;
/*!40000 ALTER TABLE `sys_role_dept` DISABLE KEYS */;
INSERT INTO `sys_role_dept` (`role_id`, `dept_id`) VALUES (2,100),(2,101),(2,105);
/*!40000 ALTER TABLE `sys_role_dept` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sys_role_menu`
--

LOCK TABLES `sys_role_menu` WRITE;
/*!40000 ALTER TABLE `sys_role_menu` DISABLE KEYS */;
INSERT INTO `sys_role_menu` (`role_id`, `menu_id`) VALUES (2,1),(2,2),(2,3),(2,4),(2,100),(2,101),(2,102),(2,103),(2,104),(2,105),(2,106),(2,107),(2,108),(2,109),(2,110),(2,111),(2,112),(2,113),(2,114),(2,115),(2,116),(2,117),(2,500),(2,501),(2,1000),(2,1001),(2,1002),(2,1003),(2,1004),(2,1005),(2,1006),(2,1007),(2,1008),(2,1009),(2,1010),(2,1011),(2,1012),(2,1013),(2,1014),(2,1015),(2,1016),(2,1017),(2,1018),(2,1019),(2,1020),(2,1021),(2,1022),(2,1023),(2,1024),(2,1025),(2,1026),(2,1027),(2,1028),(2,1029),(2,1030),(2,1031),(2,1032),(2,1033),(2,1034),(2,1035),(2,1036),(2,1037),(2,1038),(2,1039),(2,1040),(2,1041),(2,1042),(2,1043),(2,1044),(2,1045),(2,1046),(2,1047),(2,1048),(2,1049),(2,1050),(2,1051),(2,1052),(2,1053),(2,1054),(2,1055),(2,1056),(2,1057),(2,1058),(2,1059),(2,1060);
/*!40000 ALTER TABLE `sys_role_menu` ENABLE KEYS */;
UNLOCK TABLES;

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
  `email` varchar(50) DEFAULT '' COMMENT '用户邮箱',
  `phonenumber` varchar(11) DEFAULT '' COMMENT '手机号码',
  `sex` char(1) DEFAULT '0' COMMENT '用户性别（0男 1女 2未知）',
  `avatar` varchar(100) DEFAULT '' COMMENT '头像地址',
  `password` varchar(100) DEFAULT '' COMMENT '密码',
  `status` char(1) DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `login_ip` varchar(128) DEFAULT '' COMMENT '最后登录IP',
  `login_date` datetime DEFAULT NULL COMMENT '最后登录时间',
  `pwd_update_date` datetime DEFAULT NULL COMMENT '密码最后更新时间',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
INSERT INTO `sys_user` (`user_id`, `dept_id`, `user_name`, `nick_name`, `user_type`, `email`, `phonenumber`, `sex`, `avatar`, `password`, `status`, `del_flag`, `login_ip`, `login_date`, `pwd_update_date`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES (1,103,'admin','超级管理员','00','niangao@163.com','15888888888','1','','$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2','0','0','127.0.0.1','2025-10-17 12:22:19','2025-10-16 10:32:52','admin','2025-10-16 10:32:52','',NULL,'管理员'),(2,105,'niangao','年糕','00','niangao@qq.com','15666666666','1','','$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2','0','2','127.0.0.1','2025-10-16 10:32:52','2025-10-16 10:32:52','admin','2025-10-16 10:32:52','admin','2025-10-16 14:42:39','测试员'),(100,100,'朱涵威','朱涵威','00','','','0','','$2b$12$0WgIK5TpP9GuPS6WcWX7Uu5LgFpEFX9OUox1kilY7Pv5xgejQ1qw2','0','0','',NULL,NULL,'admin','2025-10-16 14:43:07','admin','2025-10-16 14:43:07',NULL);
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sys_user_post`
--

LOCK TABLES `sys_user_post` WRITE;
/*!40000 ALTER TABLE `sys_user_post` DISABLE KEYS */;
INSERT INTO `sys_user_post` (`user_id`, `post_id`) VALUES (1,1);
/*!40000 ALTER TABLE `sys_user_post` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `sys_user_role`
--

LOCK TABLES `sys_user_role` WRITE;
/*!40000 ALTER TABLE `sys_user_role` DISABLE KEYS */;
INSERT INTO `sys_user_role` (`user_id`, `role_id`) VALUES (1,1);
/*!40000 ALTER TABLE `sys_user_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'ruoyi-fastapi'
--

--
-- Dumping routines for database 'ruoyi-fastapi'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-17 12:37:26
