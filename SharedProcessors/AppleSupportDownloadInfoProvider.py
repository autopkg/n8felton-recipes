#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Nathan Felton (n8felton)
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

import urllib2
import re

from autopkglib import Processor, ProcessorError

__all__ = ["AppleSupportDownloadInfoProvider"]


class AppleSupportDownloadInfoProvider(Processor):
    description = "Provides links to downloads posted to the Apple support \
                   knowledge bases."
    input_variables = {
        "ARTICLE_NUMBER": {
            "required": True,
            "description": "The KB article number without the leading 'DL' \
                            e.g. http://support.apple.com/kb/dl907 \
                            ARTICLE_NUMBER = 907"
        },
        "LOCALE": {
            "required": False,
            "description": "The ISO-639 language code and the \
                           ISO-3166 country code \
                           e.g. en_US = English, American \
                           es_ES = Español, Spain"
        }
    }
    output_variables = {
        "url": {
            "description": "The full url for the file you want to download."
        },
        "version": {
            "description": "The version of the support download"
        }
    }

    def get_url(self, download_url):
        try:
            request = urllib2.Request(download_url)
            response = urllib2.urlopen(request)
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (download_url, e))

        return response.geturl()

    def get_html_title(self, article_url):
        """Retrieve the HTML <title> from a webpage"""

        try:
            response = urllib2.urlopen(article_url)
        except urllib2.HTTPError, e:
            raise ProcessorError("Unable to access %s: %s" % (download_url, e))
        except urllib2.URLError, e:
            raise ProcessorError("Unable to access %s: %s" % (download_url, e))

        info = response.info()
        try:
            content_type = info['Content-Type']
            if not re.match(".*/html.*", content_type):
                raise ProcessorError("Unable to access %s: %s" % (
                                     download_url, e))
        except:
            raise ProcessorError("Unable to access %s: %s" % (download_url, e))

        head = response.read(8192)
        head = re.sub("[\r\n\t ]", " ", head)

        title = re.search('(?i)\<title\>(.*?)\</title\>', head)
        if title:
            title = title.group(1)
            return title
        else:
            raise ProcessorError("Unable to determine version")

    def get_version(self):
        base_url = "http://support.apple.com"
        article_number = self.env['ARTICLE_NUMBER']
        article_url = "{base_url}/kb/DL{article_number}".format(
                      base_url=base_url,
                      article_number=article_number)
        title = self.get_html_title(article_url)
        regex = '(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)'
        match = re.search(regex, title)
        if match:
            version = match.group(0)
            self.output("Version is {version}".format(version=match.group(0)))
            return version
        else:
            raise ProcessorError("Unable to determine version.")

    def main(self):
        base_url = "http://support.apple.com"
        article_number = self.env['ARTICLE_NUMBER']
        if 'LOCALE' not in self.env:
            locale = "en_US"
        else:
            locale = self.env['LOCALE']

        download_url =\
            "{base_url}/downloads/DL{article_number}/{locale}/".format(
                base_url=base_url,
                article_number=article_number,
                locale=locale)
        full_url = self.get_url(download_url)
        self.env['url'] = full_url
        self.env['version'] = self.get_version()

if __name__ == "__main__":
    processor = AppleSupportDownloader()
    processor.execute_shell()
