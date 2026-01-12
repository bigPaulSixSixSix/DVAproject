#!/bin/bash
# 数据库迁移执行脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "数据库迁移脚本"
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
SQL_FILE="backup/apply/数据库设计SQL_MySQL.sql"
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
echo "开始执行迁移..."
echo ""

# 执行SQL脚本
if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SQL_FILE" 2>&1; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ 数据库迁移成功完成！"
    echo "==========================================${NC}"
    
    # 验证表是否创建成功
    echo ""
    echo "验证新增表..."
    TABLES=("apply_primary" "apply_rules" "apply_log" "todo_task" "todo_stage" "todo_task_apply")
    for table in "${TABLES[@]}"; do
        if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "SHOW TABLES LIKE '$table';" 2>/dev/null | grep -q "$table"; then
            echo -e "  ${GREEN}✓${NC} $table"
        else
            echo -e "  ${RED}✗${NC} $table (未找到)"
        fi
    done
else
    echo ""
    echo -e "${RED}=========================================="
    echo "❌ 数据库迁移失败"
    echo "==========================================${NC}"
    echo ""
    echo "请检查错误信息，或手动执行SQL脚本:"
    echo "  mysql -u$DB_USER -p$DB_NAME < $SQL_FILE"
    exit 1
fi
