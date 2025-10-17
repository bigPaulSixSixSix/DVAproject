# RuoYi-FastAPI 数据库迁移指南

## 📋 当前数据库状态

### 数据库信息
- **数据库名**: ruoyi-fastapi
- **表数量**: 20个
- **备份时间**: 2025-10-17 12:37:25

### 关键数据统计
| 表名 | 记录数 | 说明 |
|------|--------|------|
| sys_user | 3 | 用户表 |
| sys_role | 2 | 角色表 |
| sys_menu | 91 | 菜单表 |
| sys_dept | 23 | 部门表 |
| sys_config | 8 | 配置表 |

## 🚀 在新设备上部署

### 1. 准备工作

#### 系统要求
- Python 3.12+
- MySQL 8.0+
- Redis 6.0+

#### 安装MySQL和Redis
```bash
# macOS
brew install mysql redis
brew services start mysql
brew services start redis

# Ubuntu/Debian
sudo apt-get install mysql-server redis-server
sudo systemctl start mysql
sudo systemctl start redis-server
```

### 2. 项目部署

#### 复制项目文件
```bash
# 复制整个项目目录到新设备
scp -r ruoyi-fastapi-backend/ user@new-device:/path/to/destination/
```

#### 安装Python依赖
```bash
cd ruoyi-fastapi-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 数据库初始化

#### 方法一：使用自动脚本（推荐）
```bash
cd backup/
chmod +x init_database.sh
./init_database.sh
```

#### 方法二：手动恢复
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE \`ruoyi-fastapi\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 恢复数据
mysql -u root -p ruoyi-fastapi < backup/ruoyi-fastapi_backup_*.sql
```

### 4. 配置环境变量

创建 `.env.dev` 文件：
```bash
# 应用配置
APP_ENV=dev
APP_NAME=RuoYi-FasAPI
APP_ROOT_PATH=/dev-api
APP_HOST=0.0.0.0
APP_PORT=9099
APP_VERSION=1.0.0
APP_RELOAD=true

# JWT配置
JWT_SECRET_KEY=b01c66dc2c58dc6a0aabfe2144256be36226de378bf87f72c0c795dda67f4d55
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 数据库配置
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your-mysql-password
DB_DATABASE=ruoyi-fastapi

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DATABASE=2
```

### 5. 启动应用

```bash
source venv/bin/activate
python3 app.py
```

### 6. 验证部署

- API文档: http://localhost:9099/docs
- 应用接口: http://localhost:9099/dev-api/
- 默认管理员账号: admin / admin123

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
brew services list | grep mysql
# 或
sudo systemctl status mysql

# 测试连接
mysql -u root -p -e "SELECT 1;"
```

#### 2. Redis连接失败
```bash
# 检查Redis服务状态
brew services list | grep redis
# 或
sudo systemctl status redis

# 测试连接
redis-cli ping
```

#### 3. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :9099

# 终止进程
kill -9 <PID>
```

#### 4. 权限问题
```bash
# 给脚本添加执行权限
chmod +x backup/init_database.sh

# 检查文件权限
ls -la backup/
```

## 📁 文件清单

### 必需文件
- `backup/ruoyi-fastapi_backup_*.sql` - 数据库备份文件
- `backup/init_database.sh` - 数据库初始化脚本
- `requirements.txt` - Python依赖
- `app.py` - 应用入口
- `server.py` - 应用配置
- `config/` - 配置目录
- `module_admin/` - 管理模块
- `utils/` - 工具类

### 可选文件
- `sql/ruoyi-fastapi.sql` - 原始SQL脚本
- `sql/ruoyi-fastapi-pg.sql` - PostgreSQL版本脚本
- `requirements-pg.txt` - PostgreSQL依赖

## 📞 技术支持

如果遇到问题，请检查：
1. 数据库服务是否正常运行
2. Redis服务是否正常运行
3. 环境变量配置是否正确
4. Python依赖是否完整安装
5. 端口是否被占用

## 📝 更新日志

- 2025-10-17: 创建数据库备份和迁移指南
- 包含20个表的完整数据
- 提供自动化部署脚本

