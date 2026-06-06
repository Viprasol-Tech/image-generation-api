# Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip && python -m pip install .

EXPOSE 8000

CMD ["uvicorn", "image_generation_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
