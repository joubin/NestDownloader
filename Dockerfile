FROM selenium/standalone-firefox
USER root
WORKDIR /app
RUN apt update && apt install -y python3 python3-pip ffmpeg
COPY requirements.txt /app
COPY main.py /app
COPY download.sh /app
RUN pip install -r requirements.txt && chown seluser:seluser /app -R && chmod +x /app/download.sh
USER seluser
ENTRYPOINT [ "/app/download.sh" ]
