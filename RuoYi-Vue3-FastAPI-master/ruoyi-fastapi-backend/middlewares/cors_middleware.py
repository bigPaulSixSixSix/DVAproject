from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI):
    """
    添加跨域中间件
    允许所有源访问，无需白名单设置

    :param app: FastAPI对象
    :return:
    """
    # 后台api允许跨域（允许所有源）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有源访问
        allow_credentials=False,  # 注意：使用通配符时不能启用 credentials
        allow_methods=['*'],  # 允许所有HTTP方法
        allow_headers=['*'],  # 允许所有请求头
    )
