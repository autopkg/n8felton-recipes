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
""""Update information provider for Intel XDK"""

import urllib2
import json

from autopkglib import Processor, ProcessorError

__all__ = ["IntelXDKInfoProvider"]

XDK_BASE_URL = 'https://xdk2-installers.s3.amazonaws.com/xdk/'


class IntelXDKInfoProvider(Processor):
    """Determines the latest available version of the Intel XDK
    Provides the update URL as well as an MD5 checksum of the update"""
    description = __doc__
    input_variables = {
        "release": {
            "required": False,
            "default": 'latest',
            "description": (
                "Which release to download. Currently only 'latest' is "
                "available."),
        },
        "base_url": {
            "required": False,
            "description": "Default is {0}.".format(XDK_BASE_URL)
        },
    }
    output_variables = {
        "url": {
            "description": "The full url for the file you want to download."
        },
        "md5checksum": {
            "description": "The MD5 checksum of the file, provided by the API."
        },
    }

    @classmethod
    def get_xdk_updates(cls, updates_url):
        """Returns a JSON response using the XDK client update source"""
        try:
            request = urllib2.Request(updates_url)
            response = urllib2.urlopen(request)
        except BaseException as e:
            raise ProcessorError("Can't open %s: %s" % (updates_url, e))

        releases = json.loads(response.read())
        return releases

    def main(self):
        release = self.env.get('release', 'latest')
        base_url = self.env.get('base_url', XDK_BASE_URL)
        updates_url = "{0}{1}".format(base_url, 'updates.json')
        self.output("Updates URL: {updates_url}".format(
            updates_url=updates_url),
                    2)
        updates = self.get_xdk_updates(updates_url)
        self.output(updates, 3)
        download_url = "{0}{1}".format(base_url,
                                       updates[release]['macosx']['file'])
        self.env['url'] = download_url
        md5checksum = updates[release]['macosx']['fileMD5']
        self.env['md5checksum'] = md5checksum

if __name__ == "__main__":
    PROCESSOR = IntelXDKInfoProvider()
    PROCESSOR.execute_shell()
