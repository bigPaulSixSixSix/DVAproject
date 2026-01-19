# Docker 构建和部署指南

本文档说明如何使用 Docker 构建和部署后端和前端项目。

## 环境说明

项目支持三种环境：
- **local**: 本地测试环境（用于本地构建测试）
- **dev**: 测试环境（部署到测试服务器）
- **prod**: 生产环境（生产环境，目前为模板）

## 后端构建

### 构建命令

```bash
# 进入后端目录
cd ruoyi-fastapi-backend

# 构建本地测试环境镜像
docker build --build-arg BUILD_ENV=local -t ruoyi-backend:local .

# 构建测试环境镜像（用于部署到服务器）
docker build --build-arg BUILD_ENV=dev -t ruoyi-backend:dev .

# 构建生产环境镜像
docker build --build-arg BUILD_ENV=prod -t ruoyi-backend:prod .
```

### 运行命令

```bash
# 运行本地测试环境（配置文件已打包到镜像，无需挂载）
docker run -d \
  -p 9099:9099 \
  --name ruoyi-backend-local \
  ruoyi-backend:local

# 运行测试环境（配置文件已打包到镜像，无需挂载）
docker run -d \
  -p 9099:9099 \
  --name ruoyi-backend-dev \
  ruoyi-backend:dev

# 运行生产环境（配置文件不打包，需要挂载以保持安全）
docker run -d \
  -p 9099:9099 \
  --name ruoyi-backend-prod \
  -v $(pwd)/.env.prod:/app/.env.prod \
  ruoyi-backend:prod
```

### 注意事项

1. **配置文件打包**：
   - **local/dev 环境**：`.env.local` 和 `.env.dev` 在构建时已打包到镜像中，运行时无需挂载，命令更简洁
   - **prod 环境**：`.env.prod` 不打包到镜像（保持安全），运行时必须挂载
2. **数据库连接**：
   - local/dev 环境：如果数据库在宿主机，使用 `host.docker.internal`（macOS/Windows）或 `172.17.0.1`（Linux）
   - prod 环境：使用实际的数据库地址
3. **环境变量覆盖**：可以通过 `-e APP_ENV=local/dev/prod` 在运行时覆盖构建时的环境设置

## 前端构建

### 构建命令

```bash
# 进入前端目录
cd ruoyi-fastapi-frontend

# 构建本地测试环境镜像
docker build --build-arg BUILD_ENV=local -t ruoyi-frontend:local .

# 构建测试环境镜像（用于部署到服务器）
docker build --build-arg BUILD_ENV=dev -t ruoyi-frontend:dev .

# 构建生产环境镜像
docker build --build-arg BUILD_ENV=prod -t ruoyi-frontend:prod .
```

### 运行命令

```bash
# 运行本地测试环境
docker run -d \
  -p 80:80 \
  --name ruoyi-frontend-local \
  ruoyi-frontend:local

# 运行测试环境
docker run -d \
  -p 80:80 \
  --name ruoyi-frontend-dev \
  ruoyi-frontend:dev

# 运行生产环境
docker run -d \
  -p 80:80 \
  --name ruoyi-frontend-prod \
  ruoyi-frontend:prod
```

### 注意事项

1. **环境变量文件**：前端需要在项目根目录创建对应的 `.env.local`、`.env.dev`、`.env.prod` 文件
2. **Vite 模式**：构建时会根据 `BUILD_ENV` 自动加载对应的 `.env.{mode}` 文件
3. **API 地址配置**：确保 `.env` 文件中的 `VITE_APP_BASE_API` 等配置正确

## 前端环境变量文件示例

需要在 `ruoyi-fastapi-frontend` 目录下创建以下文件：

### .env.local（本地测试环境）
```env
# 本地环境配置
VITE_APP_ENV=local
VITE_APP_BASE_API=http://localhost:9099
```

### .env.dev（测试环境）
```env
# 测试环境配置
VITE_APP_ENV=dev
VITE_APP_BASE_API=http://your-dev-server:9099
```

### .env.prod（生产环境）
```env
# 生产环境配置
VITE_APP_ENV=production
VITE_APP_BASE_API=http://your-prod-server:9099
```

## 快速部署脚本示例

### 后端部署脚本

```bash
#!/bin/bash
# deploy-backend.sh

ENV=$1  # local, dev, 或 prod

if [ -z "$ENV" ]; then
  echo "用法: ./deploy-backend.sh [local|dev|prod]"
  exit 1
fi

cd ruoyi-fastapi-backend

# 构建镜像
docker build --build-arg BUILD_ENV=$ENV -t ruoyi-backend:$ENV .

# 停止并删除旧容器
docker stop ruoyi-backend-$ENV 2>/dev/null
docker rm ruoyi-backend-$ENV 2>/dev/null

# 运行新容器
# local 和 dev 环境：配置文件已打包，无需挂载
# prod 环境：需要挂载配置文件
if [ "$ENV" = "prod" ]; then
  docker run -d \
    -p 9099:9099 \
    --name ruoyi-backend-$ENV \
    -v $(pwd)/.env.$ENV:/app/.env.$ENV \
    ruoyi-backend:$ENV
else
  docker run -d \
    -p 9099:9099 \
    --name ruoyi-backend-$ENV \
    ruoyi-backend:$ENV
fi

echo "✅ 后端 $ENV 环境部署完成"
```

### 前端部署脚本

```bash
#!/bin/bash
# deploy-frontend.sh

ENV=$1  # local, dev, 或 prod

if [ -z "$ENV" ]; then
  echo "用法: ./deploy-frontend.sh [local|dev|prod]"
  exit 1
fi

cd ruoyi-fastapi-frontend

# 构建镜像
docker build --build-arg BUILD_ENV=$ENV -t ruoyi-frontend:$ENV .

# 停止并删除旧容器
docker stop ruoyi-frontend-$ENV 2>/dev/null
docker rm ruoyi-frontend-$ENV 2>/dev/null

# 运行新容器
docker run -d \
  -p 80:80 \
  --name ruoyi-frontend-$ENV \
  ruoyi-frontend:$ENV

echo "✅ 前端 $ENV 环境部署完成"
```

## 常用命令

### 查看容器日志
```bash
# 后端
docker logs -f ruoyi-backend-dev

# 前端
docker logs -f ruoyi-frontend-dev
```

### 停止容器
```bash
docker stop ruoyi-backend-dev ruoyi-frontend-dev
```

### 重启容器
```bash
docker restart ruoyi-backend-dev ruoyi-frontend-dev
```

### 删除容器和镜像
```bash
# 删除容器
docker rm -f ruoyi-backend-dev ruoyi-frontend-dev

# 删除镜像
docker rmi ruoyi-backend:dev ruoyi-frontend:dev
```
