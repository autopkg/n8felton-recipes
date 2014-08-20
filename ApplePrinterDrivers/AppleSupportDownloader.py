#!/usr/env python
# -*- coding: utf-8 -*-
#
# Created by Nathan Felton (n8felton)

import urllib2

from autopkglib import Processor, ProcessorError

__all__ = ["AppleSupportDownloader"]


class AppleSupportDownloader(Processor):
    description = "Provides links to downloads posted to the Apple support \
                   knowledgebases."
    input_variables = {
        "ARTICLE_NUMBER": {
            "required": True,
            "description": "The KB artical number without the leading 'DL' \
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
        }
    }

    def get_url(self, download_url):
        request = urllib2.Request(download_url)
        response = urllib2.urlopen(request)
        return response.geturl()

    def main(self):
        self.base_url = "http://support.apple.com"
        self.article_number = self.env['ARTICLE_NUMBER']
        if 'LOCALE' not in self.env:
            self.locale = "en_US"
        else:
            self.locale = self.env['LOCALE']

        self.download_url =\
            "{base_url}/downloads/DL{article_number}/{locale}/".format(
                base_url=self.base_url,
                article_number=self.article_number,
                locale=self.locale)
        self.full_url = self.get_url(self.download_url)
        self.env['url'] = self.full_url

if __name__ == "__main__":
    processor = AppleSupportDownloader()
    processor.execute_shell()
