import unittest
from unittest.mock import patch
import os, shutil

from nose.tools import assert_dict_contains_subset, assert_list_equal, assert_true

from pyfluminus.tests.mock_server import (
    get_free_port,
    start_mock_server,
    MOCK_CONSTANTS,
)
from pyfluminus.structs import Module, File
from pyfluminus import api
from pyfluminus.constants import ErrorTypes

temp_dir = "test/temp/api/file/"
id_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImEzck1VZ01Gdjl0UGNsTGE2eUYzekFrZnF1RSIsImtpZCI6ImEzck1VZ01Gdjl0UGNsTGE2eUYzekFrZnF1RSJ9.eyJpc3MiOiJodHRwczovL2x1bWludXMubnVzLmVkdS5zZy92Mi9hdXRoIiwiYXVkIjoidmVyc28iLCJleHAiOjE1NTIwMzQ4ODQsIm5iZiI6MTU1MjAzNDU4NCwibm9uY2UiOiJlYjA0Y2ZmN2U4YTg0YTM0YTlhOWE0YWI3NGU3NzE2NiIsImlhdCI6MTU1MjAzNDU4NCwiYXRfaGFzaCI6Im9RYmFrbkxxeUVPYWtWQV8tMjA2Q1EiLCJjX2hhc2giOiJfMi02T29UYjJJOUpFU2lDZEI2ZGVBIiwic2lkIjoiNTYyZGYxYWYyODRhMDA4MTY1MGE0MDQ4N2NhODAzOTgiLCJzdWIiOiIwMzA4OTI1Mi0wYzk2LTRmYWItYjA4MC1mMmFlYjA3ZWViMGYiLCJhdXRoX3RpbWUiOjE1NTIwMzQ1ODQsImlkcCI6Imlkc3J2IiwiYWRkcmVzcyI6IlJlcXVlc3QgYWxsIGNsYWltcyIsImFtciI6WyJwYXNzd29yZCJdfQ.R54fwml4-KmwaD_pNSJxmf3XXoQdf3coik7-c-Lt7dconpJHLlorsiymQaiGLTlUdvMGHYvN_1JzCi42azkCxF2kjAJiosdCigR3b4okM1sovXoJsbE7tIycx2jpZwCmusL6nMffzE0ly_Q28x55jdQmJ9PIyGe7XD4mfKqDweht4fhCAtoeJtNPeDKX2dG6p4ll0lJxgVBOZsdi8PYF6z_rTt7zmMgd9CSc6WH2sOl8f9FKpVxoGtLBmjEBcNbwODokTu-cgW20vLFc05a7UZa3uKzPZI3DONnUDptLGgatcYGmNDTooQrJdh5xDKrK1tmkgVgBTmvPb44WYIiqHw"
authorization = {"jwt": id_token}
module = Module(
    code="ST2334",
    id="40582141-1a1d-41b6-ba3a-efa44ff7fd05",
    name="Probability and Statistics",
    teaching=False,
    term="1820",
)
sample_file = File(
    id="731db9ba-b919-4614-928c-1ac7d4172b3c",
    name="Jasra, Ajay - Tut1.docx",
    directory=False,
    children=None,
    allow_upload=False,
    multimedia=False,
)


def file_equality(f1, f2, msg=None):
    assert (
        f1.id == f2.id
        and f1.name == f2.name
        and f1.directory == f2.directory
        and f1.allow_upload == f2.allow_upload
        and f1.multimedia == f2.multimedia
    ), "file attributes differ"

    if f1.children is None or f2.children is None:
        return True
    if len(f1.children) == len(f2.children) == 0:
        return True

    assert len(f1.children) == len(f2.children) and all(
        file_equality(f1_child, f2_child)
        for f1_child, f2_child in zip(f1.children, f2.children)
    ), "file children differ"

    return True


class TestFiles(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        # TODO add mock server for auth
        cls.mock_server = start_mock_server(8082)  # for API

        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            print('removed test generated files')
            shutil.rmtree(temp_dir)

    @classmethod
    def tearDownClass(cls):
        cls.mock_server.shutdown()
        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            print('removed test generated files')
            shutil.rmtree(temp_dir)

    def setUp(self):
        self.addTypeEqualityFunc(File, file_equality)

    def test_files_from_module(self):
        with patch.dict("pyfluminus.api.__dict__", MOCK_CONSTANTS):
            file = File.from_module(authorization, module)
        expected_file = File(
            id="40582141-1a1d-41b6-ba3a-efa44ff7fd05",  # id of ST2334
            name="ST2334",
            directory=True,
            children=[
                File(
                    id="7c464b62-3811-4c87-b1d1-7407e6ec321b",
                    name="Tutorial Questions",
                    directory=True,
                    children=None,
                    allow_upload=False,
                    multimedia=False,
                ),
                File(
                    id="5a9525ba-e90c-44aa-a659-267bbf508d11",
                    name="Lecture Notes",
                    directory=True,
                    children=None,
                    allow_upload=False,
                    multimedia=False,
                ),
            ],
            allow_upload=False,
            multimedia=False,
        )
        self.assertEqual(expected_file, file)

    def test_file_from_module_filename_sanitised(self):
        # ignore the fields other than code are wrong
        module = Module(
            code="CS1231/MA1100",
            id="40582141-1a1d-41b6-ba3a-efa44ff7fd05",
            name="Probability and Statistics",
            teaching=False,
            term="1820",
        )

        with patch.dict("pyfluminus.api.__dict__", MOCK_CONSTANTS):
            # file = api.get_file_from_module(authorization, module)
            file = File.from_module(authorization, module)
        self.assertEquals(file.name, "CS1231-MA1100")

    # TODO implement tests for:
    # - load children direcetory allow_upload prepends with creator name
    # - load_children directory
    # - load_children file
    # - load_children already_loaded
    # - download

    def test_get_download_url(self):
        with patch.dict("pyfluminus.api.__dict__", MOCK_CONSTANTS):
            download_url = sample_file.get_download_url(authorization)
        self.assertEqual(
            download_url,
            "http://localhost:8082/v2/api/files/download/6f3cfb8c-5b91-4d5a-849a-70dcb31eea87",
        )

    def test_download(self):
        with patch.dict("pyfluminus.api.__dict__", MOCK_CONSTANTS):
            result1 = sample_file.download(authorization, temp_dir)
            expected_filepath = os.path.join(temp_dir, sample_file.name)
            self.assertTrue(result1.okay)
            self.assertTrue(
                os.path.exists(expected_filepath),
                "cannnot find file {}".format(expected_filepath),
            )
            with open(expected_filepath, 'r') as f:
                self.assertEqual("This is just a sample file.\n", "".join(f.readlines()))
            result2 = sample_file.download(authorization, temp_dir)
            self.assertFalse(result2.okay)
            self.assertEquals(result2.error_type, ErrorTypes.FileExists)

        

