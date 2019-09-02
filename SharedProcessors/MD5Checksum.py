#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Nathan Felton (n8felton)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Calculate a message-digest fingerprint (checksum) for a file"""

from __future__ import absolute_import

import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["MD5Checksum"]


class MD5Checksum(Processor):
    """Calculate a message-digest fingerprint (checksum) for a file"""
    description = __doc__
    input_variables = {
        "pathname": {
            "required": True,
            "description": "Path of the file to calculate MD5 checksum on."
        },
        "md5checksum": {
            "required": False,
            "description": "A MD5 checksum to verify pathname."
        },
    }
    output_variables = {
        "md5checksum": {
            "description": "MD5 checksum calculated from pathname."
        },
    }

    def md5(self, file_name):
        md5 = hashlib.md5()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def main(self):
        md5checksum = self.md5(self.env["pathname"])
        self.output("{md5checksum}".format(md5checksum=md5checksum), 1)
        if self.env.get('md5checksum'):
            if not self.env['md5checksum'] == md5checksum:
                raise ProcessorError("MD5 Checksum verification failed.")
            else:
                self.output("MD5 Checksum Matches", 1)
        self.env["md5checksum"] = md5checksum

if __name__ == "__main__":
    PROCESSOR = MD5Checksum()
    PROCESSOR.execute_shell()
