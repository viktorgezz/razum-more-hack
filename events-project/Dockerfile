# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=600

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_EXTRA_INDEX_URL=
ARG PIP_TRUSTED_HOST=
ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

WORKDIR /app

COPY requirements.txt .
# Кэш pip между сборками (BuildKit); длинный таймаут и ретраи — против обрывов PyPI
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --retries 20 --timeout 600 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--chdir", "events-project", "--bind", "0.0.0.0:8000", "wsgi:application"]
