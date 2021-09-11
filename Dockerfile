FROM selenium/standalone-firefox
USER root
WORKDIR /app
RUN apt update && apt install -y python3 python3-pip ffmpeg fonts-freefont-ttf
COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt && chown seluser:seluser /app -R 
USER seluser
COPY main.py /opt/

ENTRYPOINT [ "python3" ]
CMD [ "-u", "/opt/main.py" ]
