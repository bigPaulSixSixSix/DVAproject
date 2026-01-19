# 多阶段构建 Dockerfile
# 第一阶段：构建阶段
# 说明：使用 Node 22-alpine（与本地开发环境 v22.20.0/v23.7.0 兼容）
FROM node:22-alpine AS builder

# 构建参数：指定构建环境（development/dev/prod），默认 prod
# 使用方式：
#   - 本地测试环境：docker build --build-arg BUILD_ENV=development -t frontend:local .
#   - 测试环境：docker build --build-arg BUILD_ENV=dev -t frontend:dev .
#   - 生产环境：docker build --build-arg BUILD_ENV=prod -t frontend:prod .
ARG BUILD_ENV=prod

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制项目文件
COPY . .

# 根据 BUILD_ENV 构建项目
# Vite 会根据 --mode 参数加载对应的 .env.{mode} 文件
RUN if [ "$BUILD_ENV" = "development" ]; then \
      npm run build:local; \
    elif [ "$BUILD_ENV" = "dev" ]; then \
      npm run build:dev; \
    else \
      npm run build:prod; \
    fi

# 第二阶段：运行阶段
# 使用稳定的 Nginx Alpine 镜像
FROM nginx:alpine

# 复制构建产物到 nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
