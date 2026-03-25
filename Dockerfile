# 基础镜像（官方Python免费镜像，Alpine版轻量化）
FROM python:3.10-alpine

# 设置pip源以加速下载，并配置Python环境
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 复制依赖清单
COPY requirements.txt .

# 安装依赖（使用国内源加速，Alpine版优化，避免依赖缺失）
RUN pip install --no-cache-dir -r requirements.txt 

# 复制所有代码
COPY . .

# 启动命令（运行机器人主程序）
CMD ["python", "bot.py"]