from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import subprocess
import sys
from pathlib import Path


def eprint(msg):
    sys.stderr.write(msg)


def get_stream_url(url: str) -> str:
    if url is None or url == "":
        eprint("The URL was not set as the environmental var PUBLIC_URL")
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
            eprint("The web page must have changed, please review the source code")
            sys.exit(1)
        else:
            return video_elements[0].get_attribute('src')
    finally:
        driver.quit()


def ffmpeg_stream(stream_url: str, segment_time: int = 300, output_path: str = ""):
    # This approach is insecure but easy to read
    # Ensure that url is from a trusted source
    command = "ffmpeg -i " + stream_url + " -loglevel error -f segment -segment_time " + str(
        segment_time) + " -g 10 -sc_threshold 0 " \
                        "-reset_timestamps 1 -strftime 1 %Y-%m-%d_%H-%M-%S-Garage.mp4"

    # command = "ffmpeg -i " + stream_url + "  -c copy  -f segment -segment_time 300 -strftime 1 " + \
    #     OUTPUT_DIR + "%Y-%m-%d_%H-%M-%S-Garage.mp4"
    print(command)
    subprocess.call(command, shell=True)


if __name__ == '__main__':
    while 1:
        print("Starting")
        try:
            print("Getting stream url from the NESTDOWNLOADER_PUBLIC_URL")
            stream_url = get_stream_url(
                url=os.getenv('NESTDOWNLOADER_PUBLIC_URL'))
            segment_time = os.getenv("NESTDOWNLOADER_SEGMENT_SIZE", 300)
            formatted_file_name = os.getenv(
                "NESTDOWNLOADER_FILENAME_FORMAT", "%Y-%m-%d_%H-%M-%S-Garage.mp4")
            print("Running FFMPEG")
            ffmpeg_stream(stream_url=stream_url, segment_time=segment_time)
        except Exception as e:
            print(e)
            eprint(str(e))
