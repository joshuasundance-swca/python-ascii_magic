FROM python:3.13.7-slim-trixie

RUN adduser --uid 1000 --disabled-password --gecos '' user
USER 1000

ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_NODE_PATH=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    GRADIO_NODE_PORT=7850 \
    GRADIO_ANALYTICS_ENABLED=False \
    GRADIO_SSR_MODE=True

RUN pip install --user --upgrade pip

COPY requirements.txt LICENCE README.md setup.py /home/user/python-ascii_magic/

RUN pip install --user --upgrade \
    -r /home/user/python-ascii_magic/requirements.txt

COPY ./ascii_magic /home/user/python-ascii_magic/ascii_magic
COPY ./ui /home/user/python-ascii_magic/ui

WORKDIR /home/user/python-ascii_magic
EXPOSE 7860
CMD ["python", "ui/gradio_app.py"]
