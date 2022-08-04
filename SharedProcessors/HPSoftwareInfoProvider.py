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
"""Information provider for HP software downloads."""

import json

from autopkglib import Processor, ProcessorError, URLGetter

try:
    from urllib.parse import quote  # For Python 3
except ImportError:
    from urllib2 import quote  # For Python 2

__all__ = ["HPSoftwareInfoProvider"]

HP_BASE_URL = (
    "https://h20614.www2.hp.com/ediags/solutions/software/v3?"
    "ProductNumber={product_number}&"
    "OS={os}&"
    "lc={lang_code}&"
    "cc={country_code}"
)


class HPSoftwareInfoProvider(URLGetter):
    """Determines the ESSENTIAL-REQUIRED software necessary for a given
    product_number.

    Returns the URL, version and description of the software.
    """

    description = __doc__
    input_variables = {
        "product_number": {
            "required": True,
            "description": (
                "HP Product Number of device that requires software. "
                "Typically 6 alphanumeric characters, e.g. E6B70A"
            ),
        },
        "os": {
            "required": False,
            "default": "Mac OS X 10.11",
            "description": "The OS you want to search for",
        },
        "lang_code": {
            "required": False,
            "default": "en",
            "description": "ISO 639-1 code for preferred language",
        },
        "country_code": {
            "required": False,
            "default": "us",
            "description": "ISO 3166-1 alpha-2 code for preferred country",
        },
    }
    output_variables = {
        "url": {"description": "The full url for the software."},
        "version": {"description": "The version of the software."},
        "description": {"description": "A description of the software."},
    }

    def get_hp_software_list(self, software_url):
        """Returns a JSON response using the XDK client update source."""
        response = self.download(software_url)
        releases = json.loads(response)
        return releases

    def main(self):
        """Main process."""

        # Capture input variables
        product_number = self.env.get("product_number")
        os = quote(self.env.get("os", "Mac OS X 10.11"))
        lang_code = self.env.get("lang_code", "en")
        country_code = self.env.get("country_code", "us")

        # Determine software URL
        software_url = HP_BASE_URL.format(
            product_number=product_number,
            os=os,
            lang_code=lang_code,
            country_code=country_code,
        )
        self.output("Software URL: {software_url}".format(software_url=software_url), 2)

        # Get software list and iterate through it
        software_list = self.get_hp_software_list(software_url)
        self.output(software_list, 3)
        for software in software_list:
            if software["Type"] == "ESSENTIAL-REQUIRED":
                self.env["url"] = software["FtpURL"]
                self.output(software["FtpURL"])
                self.env["version"] = software["Version"]
                self.env["description"] = software["Description"]
                # We're hoping there is only one ESSENTIAL-REQUIRED
                # but if there are multiple, we should only return the first.
                # If this becomes a problem, we'll need to test on some of the
                # other keys that are available.
                break
        # essential_required_software = software_list


if __name__ == "__main__":
    PROCESSOR = HPSoftwareInfoProvider()
    PROCESSOR.execute_shell()
