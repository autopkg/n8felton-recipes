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
"""Finds the proper file name for a download."""

import subprocess
from urllib2 import unquote
from autopkglib import Processor, ProcessorError

__all__ = ["RemoteFilenameFinder"]


class RemoteFilenameFinder(Processor):
    """Finds the proper file name for a download."""
    description = __doc__
    input_variables = {
        "url": {
            "required": True,
            "description": "The URL to retrieve the remote filename for.",
        },
        "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "filename": {
            "description": "The retrieved remote filename.",
        },
    }

    def curl_filename(self, url, curl_path=None):
        """Retrieves the remote file to determine the proper filename"""
        curl_args = ['--silent',
                     '--location',
                     '--head',
                     '--write-out', '%{url_effective}',
                     '--url', url,
                     '--output', '/dev/null']
                     
        if curl_path is None:
            curl_path = [self.env['CURL_PATH']]
        curl_cmd = curl_path + curl_args
        self.output(' '.join(curl_cmd), verbose_level=3)
        proc = subprocess.Popen(curl_cmd, shell=False, bufsize=1,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        (file_url, e) = proc.communicate()
        if e:
            raise ProcessorError(e)
        filename = file_url.rpartition("/")[2]
        return file_url, filename

    def remote_filename(self, url):
        """Finds the remote filename of the given url"""
        (file_url, filename) = self.curl_filename(url)

        # Decode any special characters in the filename, like %20 to a space.
        filename = unquote(filename)
        self.output("Found filename '{}' at '{}'".format(filename, file_url),
                    verbose_level=2)
        return filename

    def main(self):
        self.env['filename'] = self.remote_filename(self.env['url'])

if __name__ == "__main__":
    PROCESSOR = RemoteFilenameFinder()
    PROCESSOR.execute_shell()
