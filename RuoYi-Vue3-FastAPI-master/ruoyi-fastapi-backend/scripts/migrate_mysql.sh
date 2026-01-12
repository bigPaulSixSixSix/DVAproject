#!/bin/bash
# 数据库迁移脚本：为proj_task表添加审批相关字段

# 默认数据库配置（可以从.env文件读取或手动修改）
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-root1234}"
DB_NAME="${DB_NAME:-ruoyi-fastapi}"

echo "连接到数据库: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "用户: ${DB_USER}"
echo ""

# 执行SQL语句（逐个执行以便捕获错误）
echo "[1/3] 添加 approval_type 字段..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e "ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）';" 2>&1 | grep -v "Duplicate column" || echo "  字段可能已存在，跳过"

echo "[2/3] 添加 approval_levels 字段..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e "ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）';" 2>&1 | grep -v "Duplicate column" || echo "  字段可能已存在，跳过"

echo "[3/3] 更新 assignee 字段注释..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e "ALTER TABLE proj_task MODIFY COLUMN assignee VARCHAR(64) NULL COMMENT '负责人工号';" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 迁移成功完成！"
else
    echo ""
    echo "❌ 迁移失败，请检查错误信息"
    exit 1
fi
