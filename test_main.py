from unittest import TestCase
from main import *


class Test(TestCase):
    def test_archive_task(self):
        pass

    def test_get_file_paths(self):
        files = get_file_paths("./testData")
        for file in files:
            print(file)
        self.assertTrue(True)

    def test_creation_date(self):
        for file in get_file_paths("./testData"):
            print(file, creation_date(file))

    def test_create_date_chunks(self):

        files = get_file_paths("./testData")
        chunks = create_date_chunks(files=files)
        for k in chunks.keys():
            print(k, "---->")
            for f in chunks.get(k):
                print(f)

    def test_ffmpeg_contact(self):
        files = get_file_paths("./testData")
        chunks = create_date_chunks(files=files)

        for chunk in chunks.keys():
            ffmpeg_concat(chunks.get(chunk), chunk)

    def test_maintanance(self):
        maintenance()