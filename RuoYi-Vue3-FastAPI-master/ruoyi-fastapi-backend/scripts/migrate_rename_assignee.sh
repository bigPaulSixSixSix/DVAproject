#!/bin/bash
# 数据库迁移脚本：将 assignee 字段重命名为 job_number 并修复备注乱码

# 默认数据库配置
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-root1234}"
DB_NAME="${DB_NAME:-ruoyi-fastapi}"

echo "连接到数据库: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "用户: ${DB_USER}"
echo ""

# 设置字符集为utf8mb4以确保中文正确显示
export MYSQL_PWD="${DB_PASS}"

echo "[1/3] 重命名字段 assignee -> job_number..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" "${DB_NAME}" --default-character-set=utf8mb4 <<EOF
ALTER TABLE proj_task CHANGE COLUMN assignee job_number VARCHAR(64) NULL COMMENT '负责人工号';
EOF

if [ $? -ne 0 ]; then
    echo "  ⚠ 字段可能已重命名，跳过"
fi

echo "[2/3] 修复 approval_type 字段备注..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" "${DB_NAME}" --default-character-set=utf8mb4 <<EOF
ALTER TABLE proj_task MODIFY COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）';
EOF

echo "[3/3] 修复 approval_levels 字段备注..."
mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" "${DB_NAME}" --default-character-set=utf8mb4 <<EOF
ALTER TABLE proj_task MODIFY COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）';
EOF

unset MYSQL_PWD

echo ""
echo "✅ 迁移成功完成！"
