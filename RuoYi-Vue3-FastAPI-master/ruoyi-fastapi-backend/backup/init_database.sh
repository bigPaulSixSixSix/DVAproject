#!/bin/bash

# RuoYi-FastAPI 数据库初始化脚本
# 用于在新设备上快速部署数据库

echo "🚀 开始初始化 RuoYi-FastAPI 数据库..."

# 检查MySQL服务状态
if ! pgrep -x "mysqld" > /dev/null; then
    echo "❌ MySQL服务未运行，请先启动MySQL服务"
    echo "macOS: brew services start mysql"
    echo "Ubuntu: sudo systemctl start mysql"
    exit 1
fi

echo "✅ MySQL服务正在运行"

# 检查备份文件
BACKUP_FILE=$(ls backup/ruoyi-fastapi_backup_*.sql 2>/dev/null | head -1)
if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 未找到备份文件，请确保 backup/ 目录中有数据库备份文件"
    exit 1
fi

echo "📁 找到备份文件: $BACKUP_FILE"

# 读取数据库配置
read -p "请输入MySQL用户名 [root]: " DB_USER
DB_USER=${DB_USER:-root}

read -s -p "请输入MySQL密码: " DB_PASS
echo ""

read -p "请输入MySQL主机 [127.0.0.1]: " DB_HOST
DB_HOST=${DB_HOST:-127.0.0.1}

read -p "请输入MySQL端口 [3306]: " DB_PORT
DB_PORT=${DB_PORT:-3306}

# 测试数据库连接
echo "🔍 测试数据库连接..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ 数据库连接失败，请检查用户名、密码和网络连接"
    exit 1
fi

echo "✅ 数据库连接成功"

# 检查数据库是否存在
DB_NAME="ruoyi-fastapi"
if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE \`$DB_NAME\`;" 2>/dev/null; then
    echo "⚠️  数据库 '$DB_NAME' 已存在"
    read -p "是否要删除现有数据库并重新创建？(y/N): " CONFIRM
    if [[ $CONFIRM =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有数据库..."
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS \`$DB_NAME\`;"
    else
        echo "❌ 操作已取消"
        exit 1
    fi
fi

# 恢复数据库
echo "📥 开始恢复数据库..."
if mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" < "$BACKUP_FILE"; then
    echo "✅ 数据库恢复成功"
else
    echo "❌ 数据库恢复失败"
    exit 1
fi

# 验证恢复结果
echo "🔍 验证数据库恢复结果..."
TABLE_COUNT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE \`$DB_NAME\`; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';" -s -N 2>/dev/null)

if [ "$TABLE_COUNT" -eq 20 ]; then
    echo "✅ 数据库验证成功，共 $TABLE_COUNT 个表"
else
    echo "⚠️  数据库验证异常，期望20个表，实际 $TABLE_COUNT 个表"
fi

# 显示关键数据统计
echo "📊 关键数据统计:"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE \`$DB_NAME\`; SELECT 'sys_user' as table_name, COUNT(*) as count FROM sys_user UNION ALL SELECT 'sys_role', COUNT(*) FROM sys_role UNION ALL SELECT 'sys_menu', COUNT(*) FROM sys_menu UNION ALL SELECT 'sys_dept', COUNT(*) FROM sys_dept UNION ALL SELECT 'sys_config', COUNT(*) FROM sys_config;" 2>/dev/null

echo ""
echo "🎉 数据库初始化完成！"
echo ""
echo "📋 下一步操作："
echo "1. 确保Redis服务正在运行"
echo "2. 配置 .env.dev 文件中的数据库连接信息"
echo "3. 启动应用: python3 app.py"
echo "4. 访问API文档: http://localhost:9099/docs"
echo ""
echo "💡 默认管理员账号:"
echo "   用户名: admin"
echo "   密码: admin123"

