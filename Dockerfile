
FROM python:3.10-alpine

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PYTHONUNBUFFERED=1


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt 

COPY . .


CMD ["python", "bot.py"]