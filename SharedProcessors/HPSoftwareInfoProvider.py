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

from autopkglib import ProcessorError, URLGetter
from pkg_resources import packaging
from urllib.parse import urlparse, quote


__all__ = ["HPSoftwareInfoProvider"]

HP_BASE_URL = (
    "https://h20614.www2.hp.com/ediags/solutions/software/v3?"
    "{hp_query_type}={hp_query}&"
    "OS={operating_system}&"
    "lc={lang_code}&"
    "cc={country_code}"
)

HP_OPTIONAL_QUERY = (
    "&client=hp-quick-start"
)


class HPSoftwareInfoProvider(URLGetter):
    """Determines the ESSENTIAL-REQUIRED software necessary for a given
    hp_query.

    Returns the URL, version and description of the software.
    """

    description = __doc__
    input_variables = {
        "HP_QUERY_TYPE": {
            "required": True,
            "default": "ModelName",
            "description": (
                "Query type for specific product. For legacy products, this "
                "is ProductNumber, for future products, this is ModelName. "
                "Default is ModelName."
            ),
        },
        "HP_QUERY": {
            "required": True,
            "default": "HP Color LaserJet Pro M453-4",
            "description": (
                "HP Product Number or Model Name of device that requires "
                "software. For ProductNumber, this is typically 6 "
                "alphanumeric characters, e.g. E6B70A. For ModelName, this "
                "is the full product name, e.g. HP Color LaserJet Pro M453-4."
            ),
        },
        "OPERATING_SYSTEM": {
            "required": True,
            "default": "macOS 12.0",
            "description": (
                "Full name of the OS you want to search for, "
                "e.g. macOS 12.0. Default is macOS 12.0"
            ),
        },
        "LANG_CODE": {
            "required": False,
            "default": "en",
            "description": "ISO 639-1 code for preferred language",
        },
        "COUNTRY_CODE": {
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
        # Fallback to PRODUCT_NUMBER for legacy support.
        # OPERATING_SYSTEM will probably need to be set to 'Mac OS X 10.11'
        if self.env.get("PRODUCT_NUMBER"):
            hp_query_type = "ProductNumber"
            hp_query = (self.env.get("PRODUCT_NUMBER")).replace(" ", "+")
        else:
            hp_query_type = self.env.get("HP_QUERY_TYPE", "ModelName")
            hp_query = (self.env.get("HP_QUERY")).replace(" ", "+")
        operating_system = quote(self.env.get("OPERATING_SYSTEM"))
        lang_code = self.env.get("LANG_CODE", "en")
        country_code = self.env.get("COUNTRY_CODE", "us")

        # Determine software URL
        software_url = HP_BASE_URL.format(
            hp_query_type=hp_query_type,
            hp_query=hp_query,
            operating_system=operating_system,
            lang_code=lang_code,
            country_code=country_code,
        )
        # Add the additional optional query string to the URL when searching
        # for ModelName
        if hp_query_type == "ModelName":
            software_url = software_url + HP_OPTIONAL_QUERY

        self.output(f"Software URL: {software_url}", 2)

        # Get software list and iterate through it
        software_list = self.get_hp_software_list(software_url)
        self.output(software_list, 3)
        # Create a packaging.version.Version object with all zeroes.
        greatest_version = packaging.version.parse("0.0.0.0")
        recent_software = None
        for software in software_list:
            # Skip any key that isn't "ESSENTIAL-REQUIRED"
            if software["Type"] != "ESSENTIAL-REQUIRED":
                continue
            software_version = packaging.version.parse(software["Version"])
            # Find the greatest version of the HP Essentials.
            if greatest_version < software_version:
                greatest_version = software_version
                recent_software = software

        if recent_software is None:
            raise ProcessorError("Unable to find valid version of HP software")
        parsed_url = urlparse(recent_software["FtpURL"])

        # The HP ftp server rejects FTP requests now.
        if parsed_url.scheme == "ftp":
            # urllib.parse.ParseResult is a subclass of namedtuple. So it
            # is iterable.
            flat_url = "https://" + "".join([_u for _u in parsed_url[1:]])
        else:
            flat_url = parsed_url.geturl()

        self.env["url"] = flat_url
        self.output(flat_url)
        self.env["version"] = recent_software["Version"]
        self.env["description"] = recent_software["Description"]


if __name__ == "__main__":
    PROCESSOR = HPSoftwareInfoProvider()
    PROCESSOR.execute_shell()
