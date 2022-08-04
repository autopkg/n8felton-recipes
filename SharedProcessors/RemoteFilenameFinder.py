#!/usr/local/autopkg/python
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

from autopkglib import Processor, ProcessorError, URLGetter

try:
    from urllib.parse import unquote  # For Python 3
except ImportError:
    from urllib2 import unquote  # For Python 2

__all__ = ["RemoteFilenameFinder"]


class RemoteFilenameFinder(URLGetter):
    """Finds the proper file name for a download."""

    description = __doc__
    input_variables = {
        "url": {
            "required": True,
            "description": "The URL to retrieve the remote filename for.",
        },
    }
    output_variables = {
        "filename": {"description": "The retrieved remote filename.",},
    }

    def remote_filename(self, url):
        """Finds the remote filename of the given url"""

        # Build the curl command
        curl_cmd = self.prepare_curl_cmd()
        curl_cmd.extend(['--silent',
                         '--location',
                         '--head',
                         '--write-out', '%{url_effective}',
                         '--url', url,
                         '--output', '/dev/null'])

        # Use the output of curl to determine the filename
        file_url = self.download_with_curl(curl_cmd)
        filename = file_url.rpartition("/")[2]

        # If the final Location contains a query string, remove it.
        # e.g SomeAwesomeInstaller.pkg?Signature=uRznpT%2BkSK4WfaSl8kXUR7eeHqM
        # becomes just 'SomeAwesomeInstaller.pkg'
        if "?" in filename:
            filename = filename.rpartition("?")[0]

        # Decode any special characters in the filename, like %20 to a space.
        filename = unquote(filename)
        self.output("Found filename '{}' at '{}'".format(filename, file_url),
                    verbose_level=2)

        return filename

    def main(self):
        self.env["filename"] = self.remote_filename(self.env["url"])


if __name__ == "__main__":
    PROCESSOR = RemoteFilenameFinder()
    PROCESSOR.execute_shell()
