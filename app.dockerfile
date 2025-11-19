# --- Stage 1: Build Stage (用于安装依赖) ---
# 使用 Python 3.13 基础镜像
FROM python:3.13-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装 pipenv
# 需要先安装 pipenv 才能读取 Pipfile.lock
RUN pip install pipenv

# 复制 Pipfile 和 Pipfile.lock 文件
# 这是为了利用 Docker 的缓存机制
COPY Pipfile Pipfile.lock /app/

# 安装依赖
# --system: 告诉 pipenv 不要创建虚拟环境，直接安装到容器的全局环境
# --deploy: 确保安装与 Pipfile.lock 完全一致的版本
# --dev: 如果不需要 dev 依赖，可以移除此参数
RUN PIPENV_VENV_IN_PROJECT=off pipenv install --system --deploy 


# 1. 创建一个 UID 和 GID 都是 1000 的用户 (替换为您在步骤 1 中查到的数字)
# -u 1000: 指定用户 ID (UID)
# -g 134: 指定组 ID (GID)
RUN groupadd -g 134 appuser && useradd -r -u 1000 -g appuser appuser

# 2. 赋予该用户对工作目录的访问权限
RUN chown -R appuser:appuser /app

# 3. 切换到非 root 用户
USER appuser

# 复制应用程序代码和所有共享文件
COPY . .

# 定义容器启动时执行的命令 (请根据您的实际主应用文件修改)
CMD ["python", "-m", "src.main", "proddocker"]