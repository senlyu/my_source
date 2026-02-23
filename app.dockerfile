# --- Stage 1: Build Stage (用于安装依赖) ---
# 使用 Python 3.13 基础镜像
FROM python:3.13-slim AS builder

# 设置环境变量，阻止 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 设置 Python 输出不缓冲，有助于实时查看日志
ENV PYTHONUNBUFFERED 1

# 安装必要的系统依赖 (如 build-essential, git 等)
# 也可以在这里安装 pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && pip install pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 Pipfile 和 Pipfile.lock 文件
# 这是为了利用 Docker 的缓存机制
COPY Pipfile Pipfile.lock /app/

# 安装依赖到临时的虚拟环境或系统路径
# 这里安装到 /usr/local/lib/python3.13/site-packages
RUN PIPENV_VENV_IN_PROJECT=off pipenv install --system --deploy 


# --- Stage 2: Runtime Stage (精简运行环境) ---
# 使用相同的基础镜像，但没有构建工具
FROM python:3.13-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=America/Los_Angeles

# 创建非 root 用户
# 使用更常见的 UID/GID 1000:1000
RUN groupadd -r appuser && useradd -r -u 1000 -g appuser appuser

# 设置工作目录并确保权限
WORKDIR /app
RUN chown appuser:appuser /app

# 复制构建阶段安装的依赖
# 使用 --chown 确保所有权正确
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 切换到非 root 用户
USER appuser

# 复制应用程序代码
# 使用 --chown 确保所有权正确
COPY --chown=appuser:appuser . .

# 定义容器启动时执行的命令 (请根据您的实际主应用文件修改)
# 注意：config.json 将通过 volume 挂载，而不是复制到镜像中
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["prod"]