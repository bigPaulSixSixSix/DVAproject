#!/bin/bash
# 修复 apply_rules、apply_log、todo_task 表的字段注释乱码问题

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "修复表字段注释乱码"
echo "=========================================="
echo ""

# 读取数据库配置（从环境变量或使用默认值）
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-root1234}
DB_NAME=${DB_NAME:-ruoyi-fastapi}

echo "数据库配置:"
echo "  主机: $DB_HOST"
echo "  端口: $DB_PORT"
echo "  用户: $DB_USER"
echo "  数据库: $DB_NAME"
echo ""

# 检查SQL文件
SQL_FILE="scripts/fix_apply_tables_comments.sql"
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}错误: SQL文件不存在: $SQL_FILE${NC}"
    exit 1
fi

echo "SQL文件: $SQL_FILE"
echo ""

# 测试数据库连接
echo "测试数据库连接..."
if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE \`$DB_NAME\`;" 2>/dev/null; then
    echo -e "${GREEN}✓ 数据库连接成功${NC}"
else
    echo -e "${RED}✗ 数据库连接失败${NC}"
    echo "请检查数据库配置或手动执行SQL脚本"
    exit 1
fi

echo ""
echo "开始执行修复..."
echo ""

# 执行SQL脚本（使用utf8mb4字符集）
if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 "$DB_NAME" < "$SQL_FILE" 2>&1; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ 字段注释修复成功完成！"
    echo "==========================================${NC}"
    
    # 验证字段注释是否修复成功
    echo ""
    echo "验证字段注释..."
    
    # 检查 apply_rules 表
    COMMENT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 "$DB_NAME" -sN -e "SELECT COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME='apply_rules' AND COLUMN_NAME='id';" 2>/dev/null)
    if [[ "$COMMENT" == *"主键"* ]] || [[ "$COMMENT" == "主键ID" ]]; then
        echo -e "  ${GREEN}✓${NC} apply_rules 表注释已修复"
    else
        echo -e "  ${YELLOW}⚠${NC} apply_rules 表注释可能未完全修复"
    fi
    
    # 检查 apply_log 表
    COMMENT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 "$DB_NAME" -sN -e "SELECT COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME='apply_log' AND COLUMN_NAME='id';" 2>/dev/null)
    if [[ "$COMMENT" == *"主键"* ]] || [[ "$COMMENT" == "主键ID" ]]; then
        echo -e "  ${GREEN}✓${NC} apply_log 表注释已修复"
    else
        echo -e "  ${YELLOW}⚠${NC} apply_log 表注释可能未完全修复"
    fi
    
    # 检查 todo_task 表
    COMMENT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 "$DB_NAME" -sN -e "SELECT COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME='todo_task' AND COLUMN_NAME='id';" 2>/dev/null)
    if [[ "$COMMENT" == *"主键"* ]] || [[ "$COMMENT" == "主键ID" ]]; then
        echo -e "  ${GREEN}✓${NC} todo_task 表注释已修复"
    else
        echo -e "  ${YELLOW}⚠${NC} todo_task 表注释可能未完全修复"
    fi
    
else
    echo ""
    echo -e "${RED}=========================================="
    echo "❌ 字段注释修复失败"
    echo "==========================================${NC}"
    echo ""
    echo "请检查错误信息，或手动执行SQL脚本:"
    echo "  mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p --default-character-set=utf8mb4 $DB_NAME < $SQL_FILE"
    exit 1
fi
