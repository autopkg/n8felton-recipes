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
"""Shared processor to allow recipes to download Apple support downloads."""

from __future__ import absolute_import
import urllib2
import re

from autopkglib import Processor, ProcessorError

__all__ = ["AppleSupportDownloadInfoProvider"]

APPLE_SUPPORT_URL = "https://support.apple.com"


class AppleSupportDownloadInfoProvider(Processor):
    ("Provides links to downloads posted to the Apple support knowledge "
     "bases.")
    description = __doc__
    input_variables = {
        "ARTICLE_NUMBER": {
            "required": True,
            "description": ("The KB article number without the leading 'DL' "
                            "e.g. https://support.apple.com/kb/dl907 "
                            "ARTICLE_NUMBER = 907"),
        },
        "LOCALE": {
            "required": False,
            "description": ("The ISO-639 language code and the "
                            "ISO-3166 country code "
                            "e.g. en_US = English, American "
                            "es_ES = Español, Spain"),
        }
    }
    output_variables = {
        "article_url": {
            "description": ("The url for the KB article related to the "
                            "download."),
        },
        "url": {
            "description": "The full url for the file you want to download."
        },
        "version": {
            "description": "The version of the support download"
        }
    }

    @classmethod
    def get_url(cls, download_url):
        """Follows HTTP 302 redirects to fetch the final url of a download."""
        try:
            request = urllib2.Request(download_url)
            response = urllib2.urlopen(request)
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (download_url, e))

        return response.geturl()

    @classmethod
    def get_html_title(cls, article_url):
        """Retrieve the HTML <title> from a webpage"""

        try:
            response = urllib2.urlopen(article_url)
        except urllib2.HTTPError as e:
            raise ProcessorError("Unable to access %s: %s" % (article_url, e))
        except urllib2.URLError as e:
            raise ProcessorError("Unable to access %s: %s" % (article_url, e))

        info = response.info()
        try:
            content_type = info['Content-Type']
            if not re.match(".*/html.*", content_type):
                raise ProcessorError("Unable to access %s: %s" % (article_url,
                                                                  e))
        except:
            raise ProcessorError("Unable to access %s: %s" % (article_url, e))

        head = response.read(8192)
        head = re.sub("[\r\n\t ]", " ", head)

        title = re.search(r'(?i)\<title\>(.*?)\</title\>', head)
        if title:
            title = title.group(1)
            return title
        else:
            raise ProcessorError("Unable to determine version")

    def get_version(self):
        """Retrives the version of the download from the article title."""
        article_url = self.env['article_url']
        title = self.get_html_title(article_url)
        regex = r'(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)'
        match = re.search(regex, title)
        if match:
            version = match.group(0)
            self.output("Version is {version}".format(version=match.group(0)),
                        2)
            return version
        else:
            raise ProcessorError("Unable to determine version.")

    def main(self):
        article_number = self.env['ARTICLE_NUMBER']
        if 'LOCALE' not in self.env:
            locale = "en_US"
        else:
            locale = self.env['LOCALE']

        article_url = "{base_url}/kb/DL{article_number}".format(
            base_url=APPLE_SUPPORT_URL,
            article_number=article_number)
        self.env['article_url'] = article_url
        self.output("Article URL: {article_url}".format(
            article_url=article_url),
                    2)

        download_url =\
            "{base_url}/downloads/DL{article_number}/{locale}/&".format(
                base_url=APPLE_SUPPORT_URL,
                article_number=article_number,
                locale=locale)
        self.output("Download URL: {download_url}".format(
            download_url=download_url),
                    2)
        full_url = self.get_url(download_url)
        self.output("Full URL: {full_url}".format(
            full_url=full_url),
                    2)
        self.env['url'] = full_url
        self.env['version'] = self.get_version()

if __name__ == "__main__":
    PROCESSOR = AppleSupportDownloadInfoProvider()
    PROCESSOR.execute_shell()
