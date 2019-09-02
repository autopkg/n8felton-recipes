#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Nathan Felton (n8felton)
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

__all__ = ["SHA1Checksum"]


class SHA1Checksum(Processor):
    """Calculate a message-digest fingerprint (checksum) for a file"""
    description = __doc__
    input_variables = {
        "pathname": {
            "required": True,
            "description": "Path of the file to calculate SHA1 checksum on."
        },
        "sha1checksum": {
            "required": False,
            "description": "A SHA1 checksum to verify pathname."
        },
    }
    output_variables = {
        "sha1checksum": {
            "description": "SHA1 checksum calculated from pathname."
        },
    }

    def sha1(self, file_name):
        sha1 = hashlib.sha1()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1.update(chunk)
        return sha1.hexdigest()

    def main(self):
        sha1checksum = self.sha1(self.env["pathname"])
        self.output("{sha1checksum}".format(sha1checksum=sha1checksum), 1)
        if self.env.get('sha1checksum'):
            if not self.env['sha1checksum'] == sha1checksum:
                raise ProcessorError("SHA1 Checksum verification failed.")
            else:
                self.output("SHA1 Checksum Matches", 1)
        self.env["sha1checksum"] = sha1checksum

if __name__ == "__main__":
    PROCESSOR = SHA1Checksum()
    PROCESSOR.execute_shell()
