FROM selenium/standalone-firefox
USER root
WORKDIR /app
RUN apt update && apt install -y python3 python3-pip ffmpeg
COPY requirements.txt /tmp
COPY main.py /opt/

RUN pip install -r /tmp/requirements.txt && chown seluser:seluser /app -R 
USER seluser

ENTRYPOINT [ "python3" ]
CMD [ "-u", "/opt/main.py" ]
