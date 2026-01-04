FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（二进制，非常快）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uv 默认安装在 ~/.cargo/bin
ENV PATH="/root/.cargo/bin:$PATH"

# 先复制 pyproject.toml（利用缓存）
COPY pyproject.toml ./

# 用 uv 安装项目（依赖 + 包）
RUN uv pip install --system -e .

# 再复制源码
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
