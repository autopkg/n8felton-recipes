#!/usr/local/autopkg/python
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

import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["SHA256Checksum"]


class SHA256Checksum(Processor):
    """Calculate a message-digest fingerprint (checksum) for a file"""
    description = __doc__
    input_variables = {
        "pathname": {
            "required": True,
            "description": "Path of the file to calculate SHA256 checksum on."
        },
        "sha256checksum": {
            "required": False,
            "description": "A SHA256 checksum to verify pathname."
        },
    }
    output_variables = {
        "sha256checksum": {
            "description": "SHA256 checksum calculated from pathname."
        },
    }

    def sha256(self, file_name):
        sha256 = hashlib.sha256()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def main(self):
        sha256checksum = self.sha256(self.env["pathname"])
        self.output("{sha256checksum}".format(sha256checksum=sha256checksum), 1)
        if self.env.get('sha256checksum'):
            if not self.env['sha256checksum'] == sha256checksum:
                raise ProcessorError("SHA256 Checksum verification failed.")
            else:
                self.output("SHA256 Checksum Matches", 1)
        self.env["sha256checksum"] = sha256checksum

if __name__ == "__main__":
    PROCESSOR = SHA256Checksum()
    PROCESSOR.execute_shell()
