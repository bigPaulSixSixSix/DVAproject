# 数据库初始化文件说明

## ⚠️ 重要警告

**这些SQL文件包含完整的数据库结构定义，执行时会删除现有表并重新创建！**

**在生产环境使用前，请务必：**
1. 备份现有数据库
2. 确认当前数据库中的数据是否需要保留
3. 在测试环境先验证SQL文件

---

## 📁 文件说明

### ruoyi-fastapi.sql
- **数据库类型**: MySQL
- **用途**: MySQL数据库完整初始化脚本
- **包含内容**: 
  - 所有表的CREATE TABLE语句
  - 所有索引定义
  - 所有外键约束
  - 表注释和字段注释

### ruoyi-fastapi-pg.sql
- **数据库类型**: PostgreSQL
- **用途**: PostgreSQL数据库完整初始化脚本
- **包含内容**: 
  - 所有表的CREATE TABLE语句
  - 所有索引定义
  - 所有外键约束
  - 表注释和字段注释

---

## 📋 数据库表清单

本数据库包含以下主要表：

### 系统管理模块 (sys_*)
- `sys_user` - 用户信息表
- `sys_user_local` - 本地用户表
- `sys_role` - 角色信息表
- `sys_menu` - 菜单权限表
- `sys_dept` - 部门表
- `sys_config` - 参数配置表
- `sys_dict_type` - 字典类型表
- `sys_dict_data` - 字典数据表
- `sys_job` - 定时任务调度表
- `sys_job_log` - 定时任务调度日志表
- `sys_logininfor` - 系统访问记录
- `sys_oper_log` - 操作日志记录
- `sys_notice` - 通知公告表
- `sys_role_menu` - 角色和菜单关联表
- `sys_role_dept` - 角色和部门关联表
- `sys_user_role` - 用户和角色关联表
- `sys_user_post` - 用户与岗位关联表

### OA模块 (oa_*)
- `oa_department` - 部门表（真实表）
- `oa_employee_primary` - 员工主表（真实表）
- `oa_rank` - 职级表（真实表）

### 项目任务模块 (proj_*, todo_*)
- `proj_stage` - 项目阶段表
- `proj_task` - 项目任务表
- `todo_stage` - 阶段执行表
- `todo_task` - 任务执行表
- `todo_task_apply` - 任务申请详情表

### 审批模块 (apply_*)
- `apply_primary` - 申请主表
- `apply_log` - 审批日志表
- `apply_rules` - 审批规则表

### 代码生成模块 (gen_*)
- `gen_table` - 代码生成业务表
- `gen_table_column` - 代码生成业务表字段

### 其他
- `apscheduler_jobs` - 定时任务表（APScheduler）

---

## 🚀 使用方法

### MySQL数据库初始化

```bash
# 方法1: 使用mysql命令行
mysql -u root -p ruoyi-fastapi < database_init/ruoyi-fastapi.sql

# 方法2: 使用mysql客户端
mysql -u root -p
use ruoyi-fastapi;
source database_init/ruoyi-fastapi.sql;
```

### PostgreSQL数据库初始化

```bash
# 使用psql命令行
psql -U postgres -d ruoyi-fastapi -f database_init/ruoyi-fastapi-pg.sql
```

---

## 📝 注意事项

1. **数据丢失风险**: 执行这些SQL文件会删除所有现有表，请确保已备份重要数据
2. **字符集**: 所有表使用 `utf8mb4` 字符集和 `utf8mb4_0900_ai_ci` 排序规则
3. **存储引擎**: MySQL表使用 `InnoDB` 存储引擎
4. **自增起始值**: 所有表的AUTO_INCREMENT值已重置为1
5. **外键约束**: 部分表包含外键约束，请按正确顺序执行

---

## 🔄 更新记录

- **2026-01-12**: 从当前开发数据库导出最新表结构
  - 包含所有新增和修改的表
  - 修复了字段注释编码问题
  - 统一了AUTO_INCREMENT起始值

---

## 📞 联系支持

如有问题，请联系数据库管理员或开发团队。

