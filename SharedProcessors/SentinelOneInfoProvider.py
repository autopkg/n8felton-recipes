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
"""Information provider for SentinelOne Management consoles"""

import json
import logging
from urllib.parse import urlencode

from autopkglib import ProcessorError, URLGetter

__all__ = ["SentinelOneInfoProvider"]


class SentinelOneInfoProvider(URLGetter):
    ("Provides information available from the S1 Management APIs")
    description = __doc__
    input_variables = {
        "S1_CONSOLE_HOSTNAME": {
            "required": True,
            "description": "The hostname of the console you're connecting to",
        },
        "S1_API_TOKEN": {
            "required": True,
            "description":
                ("API Token generated in the console for your user account.")
        },
        "S1_PACKAGE_STATUS": {
            "required": False,
            "description":
                ("The preferred package status to filter available packages "
                 "with. Default: None (grab all available packages)")
        },
        "S1_PACKAGE_VERSION": {
            "required": False,
            "description":
                ("The preferred package version to filter available packages "
                 "with. Default: None (grab all available versions)")
        }
    }
    output_variables = {
        "url": {
            "description": "The full url of the package to download."
        },
        "filename": {
            "description": "The filename the downloaded package."
        },
        "version": {
            "description": "The version of the software."
        },
        "sha1": {
            "description": "A description of the software."
        },
    }

    def get_s1_updates(self, s1_pkg_status=None, s1_pkg_version=None):
        ("""Returns a JSON response of available agents from the SentinelOne
        API""")
        update_args = {
            "osTypes":   "macos",
            "sortBy":    "version",
            "sortOrder": "desc",
            "limit":     1,
        }

        if s1_pkg_status:
            update_args["status"] = s1_pkg_status
        if s1_pkg_version:
            update_args["version"] = s1_pkg_version
        self.output(json.dumps(update_args,
                               sort_keys=True,
                               indent=4,
                               separators=(',', ': ')),
                    2)

        api_headers = {"Authorization": f"ApiToken {self.env.get('S1_API_TOKEN')}"}

        hostname = self.env.get("S1_CONSOLE_HOSTNAME")
        query = urlencode(update_args)
        url = f"https://{hostname}/web/api/v2.1/update/agent/packages?{query}"

        response = self.download(url, headers=api_headers)
        updates_json = json.loads(response)

        self.output(json.dumps(updates_json,
                               sort_keys=True,
                               indent=4,
                               separators=(',', ': ')),
                    2)
        return updates_json

    def main(self):
        # disable module debug logging if we're not looking for debug logging
        if not self.env.get('verbose') == '3':
            logger = logging.getLogger()
            logger.setLevel(logging.WARNING)
        updates_json = self.get_s1_updates(self.env.get("S1_PACKAGE_STATUS"),
                                           self.env.get("S1_PACKAGE_VERSION"))
        try:
            s1_package = updates_json["data"][0]
        except IndexError:
            raise ProcessorError("No packages were found.")

        self.env['url'] = s1_package['link']
        self.env['filename'] = s1_package['fileName']
        self.env['version'] = s1_package['version']
        self.env['sha1'] = s1_package['sha1']


if __name__ == "__main__":
    PROCESSOR = SentinelOneInfoProvider()
    PROCESSOR.execute_shell()
