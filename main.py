from datetime import datetime, timedelta
from threading import Thread
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import subprocess
import sys
from pathlib import Path
import logging
from sys import stdout
import sched, time

CHUNK_FORMAT = "%Y%m%d"
# Define logger
logger = logging.getLogger('mylogger')

logger.setLevel(logging.DEBUG)  # set logger level
formatter = logging.Formatter("%(asctime)s %(message)s",
                              "%Y-%m-%d %H:%M:%S")
consoleHandler = logging.StreamHandler(stdout)  # set streamhandler to stdout
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


def get_file_paths(directory: str) -> List:
    from os import listdir
    from os.path import isfile, join
    import re
    files = ["{parent}{os_sep}{file}".format(parent=Path(directory).absolute(), os_sep=os.path.sep, file=f)
             for f in listdir(directory) if isfile(join(directory, f)) and re.match(r'^\d{8}', f)]
    files.sort()
    return files


def creation_date(path_to_file) -> datetime:
    from datetime import datetime

    # We name files with YYYYMMDD so we take the first 8 chars
    file_name = Path(path_to_file).name[0:14]

    date = datetime.strptime(file_name, '%Y%m%d%H%M%S')
    return date


def create_date_chunks(files: List):
    results = {}
    for file in files:
        cd = creation_date(file)
        index = cd.strftime(CHUNK_FORMAT)
        try:
            results[index].append(file)
        except:
            results[index] = [file]
    return results


def get_stream_url(url: str) -> str:
    if url is None or url == "":
        logger.error("The URL was not set as the environmental var PUBLIC_URL")
        sys.exit(1)
    ff_options = webdriver.FirefoxOptions()
    ff_options.headless = True
    driver = webdriver.Firefox(options=ff_options)

    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

        video_elements = element.find_elements_by_css_selector("*")
        if len(video_elements) != 1:
            logger.error(
                "The web page must have changed, please review the source code")
            sys.exit(1)
        else:
            # video_elements[0].click()
            return video_elements[0].get_attribute('src')
    finally:
        driver.quit()


def ffmpeg_timelaps(file, basename: str, timelaps_postfix: str = "-timelaps", speedup: str = "N/(5*TB)"):
    command = f"ffmpeg -y -discard nokey -i {file} -crf 20 -r 60 -filter:v \"setpts={speedup}\" -an {basename}{timelaps_postfix}.mp4"
    logger.debug(f"Starting timelaps creation for {file}")
    return subprocess.call(command, shell=True)


def ffmpeg_concat(files, base_name):
    import tempfile
    temp = tempfile.NamedTemporaryFile(delete=False)
    logger.info(f"File Exists {Path(temp.name).exists()}")
    for file in files:
        temp.write(bytes("file {path}\n".format(path=file), "utf-8"))
        temp.flush()
    for line in temp.readlines():
        logger.info(f"line1 {line}")
    command = f"ffmpeg -y -speed 8 -preset ultrafast -safe 0 -f concat -i {temp.name}  {base_name}.mp4"
    logger.info(f"ffmpeg_concat will run with the following command \n\t{command}")
    return subprocess.call(command, shell=True), f"{base_name}.mp4"


def ffmpeg_stream(stream_url: str, segment_time: int = 300, output_path: str = ""):
    # This approach is insecure but easy to read
    # Ensure that url is from a trusted source
    command = "ffmpeg -y -i " + stream_url + "-xerror -vf drawtext=fontfile=/usr/share/fonts/truetype/freefont" \
                                             "/FreeMonoBold.ttf" \
                                             "-user-agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                                             "(KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36 \"" \
                                             ":text='%{localtime}':fontcolor=white@0.8:x=7:y=7 -map 0:1 -map 0:2 " \
                                             "-loglevel error -f segment -segment_time " + str(
        segment_time) + " -g 10 -sc_threshold 0 " \
                        "-reset_timestamps 1 -strftime 1 %Y%m%d%H%M%S-Garage.mp4"

    logger.info(command)
    return subprocess.call(command, shell=True)


def download():
    logger.info("Starting")
    while 1:
        try:
            logger.info(
                "Getting stream url from the NESTDOWNLOADER_PUBLIC_URL")
            stream_url = get_stream_url(
                url=os.getenv('NESTDOWNLOADER_PUBLIC_URL'))
            segment_time = os.getenv("NESTDOWNLOADER_SEGMENT_SIZE", 300)
            logger.info("Running FFMPEG")
            ffmpeg_stream(stream_url=stream_url, segment_time=segment_time)
        except Exception as e:
            logger.error(e)
            logger.info("Will try to restart")


def maintenance(working_dir: str):
    # List all of the files
    logger.info("Starting Maint")
    files = get_file_paths(working_dir)
    days_ago = datetime.combine(datetime.now(), datetime.min.time()) - timedelta(
        days=os.getenv("NESTDOWNLOADER_ARCHIVE_DAYS", 10))
    # chunk into days
    chunks = create_date_chunks(files=files)
    logger.info(chunks)
    for chunk in chunks.keys():
        # filter out files not yet old enough.
        chunk_date = datetime.strptime(chunk, CHUNK_FORMAT)
        if days_ago <= chunk_date:
            logger.info(f"Condensing videos from {chunk}")
            videos = chunks.get(chunk)
            videos.sort()
            result, filename = ffmpeg_concat(videos, chunk)
            if result == 0:
                # Create a timelaps

                ffmpeg_timelaps(filename, basename=Path(filename).name.replace(".mp4", ""))
            else:
                logger.info(f"Failed to concat videos for {chunk}")
        else:
            logger.info(f"Keeping {chunks.get(chunk)}")

    # for each day, take the files and use ffmpeg to concatentate them together
    # delete the files for the given day
    # zip the concatenated single day file
    pass


if __name__ == '__main__':
    thread1 = Thread(target=download)
    thread2 = Thread(target=maintenance, args=("/app",))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    logger.info("Ending Program")
