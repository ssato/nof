#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path
import os
import shutil

import werkzeug.datastructures as WD
import nof.main.utils
import nof.main.views as TT

from .. import common as C


class Views_TestCase(C.BluePrintTestCaseWithWorkdir):

    def _assert_txt_in_resp_data(self, page, path="/"):
        txt = TT.SUMMARIES[page].encode("utf-8")
        resp = self.client.get(path)

        self.assertTrue(txt in resp.data)

    def test_10_index(self):
        self._assert_txt_in_resp_data("index", "/")

    def test_20_index_upload__post(self):
        C.skip_test()  # TODO

        for filepath in C.ok_yml_files():
            self.assertTrue(os.path.exists(filepath))
            filename = os.path.basename(filepath)

            upfile = WD.FileStorage(stream=open(filepath, "rb"),
                                    filename=filename,
                                    content_type="application/yaml")
            resp = self.client.post("/", data=dict(files=upfile),
                                    content_type="multipart/form-data")

            self.assertEqual(resp.status_code, 200, resp)

            uppath = nof.main.utils.processed_filepath(filename)
            self.assertTrue(os.path.exists(uppath))

    def test_40_finder__get(self):
        for filepath in C.ok_yml_files():
            filename = os.path.basename(filepath)
            shutil.copy(filepath, nof.main.utils.uploaddir())

            resp = self.client.get("/finder/paths/" + filename)
            self.assertEqual(resp.status_code, 200, resp)

            resp = self.client.get("/finder/networks/" + filename)
            self.assertEqual(resp.status_code, 200, resp)

# vim:sw=4:ts=4:et:
