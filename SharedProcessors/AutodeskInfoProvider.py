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
"Shared processor to provide information relevant to Autodesk products."

import urllib2
import re
import pprint
import simplejson as json

from autopkglib import Processor, ProcessorError

__all__ = ["AutodeskInfoProvider"]

AUTODESK_EDU_FREE_SOFTWARE_URL = ("https://www.autodesk.com/education/"
                                  "free-software/{0}")


class AutodeskInfoProvider(Processor):
    ("Provides the URL to the latest available version of \"PRODUCT_NAME\"")
    description = __doc__
    input_variables = {
        "PRODUCT_NAME": {
            "required": True,
            "description":
                ("The Autodesk product name. e.g. "
                 "`https://www.autodesk.com/education/free-software/autocad` "
                 "would use `autocad`.")
        },
        "OS": {
            "required": False,
            "description":
                ("The Operating System you wish to download the product for."
                 "'Win32', 'Win64', 'MacOSX' "
                 "Default: 'MacOSX'")
        },
        "LOCALE": {
            "required": False,
            "description": ("A IETF language tag based on RFC 5646."
                            "e.g. en-US = English (United States) "
                            "es-ES = Español (Spain). "
                            "Default: 'en-US'"),
        },
    }
    output_variables = {
        "url": {
            "description": "The full url for the file you want to download."
        },
    }

    @classmethod
    def get_product_releases(cls, product_url):
        """Returns the JSON of available releases for a given product_name"""
        try:
            request = urllib2.Request(product_url)
            response = urllib2.urlopen(request).read()
        except BaseException as e:
            raise ProcessorError("Can't open %s: %s" % (product_url, e))

        releases = re.search('{"releases".*}', response).group()
        releases = json.loads(releases)["releases"]
        return releases

    @classmethod
    def get_latest_release_for_os(cls, releases, operating_system, locale):
        ("Returns the latest release for a given OS given a list of releases")
        product_releases = []
        for release in releases:
            for product_release in release.get("releases"):
                product_os = product_release.get("operatingSystem")
                if (operating_system in product_os and
                        locale in product_release.get("locale")):
                    product_releases.append(product_release)
        # The eulaId appears to be the year the product was released, so we
        # sort on this to ensure we get the latest release at the end of the
        # list.
        product_releases = sorted(product_releases, key=lambda d: d["eulaId"])
        return product_releases[-1]

    def set_default_input_variable(self, variable, value):
        ("Helper function to set default value to processor variables")
        if variable not in self.env:
            self.output("{variable}: {value} (default)".format(
                variable=variable,
                value=value),
                        2)
            self.env[variable] = value
        else:
            self.output("{variable}: {value}".format(variable=variable,
                                                     value=self.env.get(
                                                         variable)),
                        2)

    def main(self):
        self.set_default_input_variable('OS', 'MacOSX')
        self.set_default_input_variable('LOCALE', 'en-US')

        product_url = AUTODESK_EDU_FREE_SOFTWARE_URL.format(
            self.env['PRODUCT_NAME'])
        self.output("Product URL: {product_url}".format(
            product_url=product_url),
                    2)

        releases = self.get_product_releases(product_url)

        latest_release = self.get_latest_release_for_os(
            releases,
            self.env.get('OS'),
            self.env.get('LOCALE'))
        self.output(pprint.pformat(latest_release), 3)
        self.env['url'] = latest_release["browserDownloadUris"][0]

if __name__ == "__main__":
    PROCESSOR = AutodeskInfoProvider()
    PROCESSOR.execute_shell()
