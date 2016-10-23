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

import subprocess

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

    def main(self):
        md5 = ['/sbin/md5',
               '-q',
               self.env["pathname"]]
        proc = subprocess.Popen(md5,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (md5checksum, e) = proc.communicate()
        # Remove the newline character from the output
        md5checksum = md5checksum.strip()
        if e:
            raise ProcessorError(e)
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
