#!/usr/local/autopkg/python
#
# Copyright 2019 Nathan Felton (n8felton)
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
"""Information provider using the Distribution file of product bundles."""

import os
import xml.etree.ElementTree as ET

from autopkglib import Processor, ProcessorError

__all__ = ["DistributionInfoProvider"]


class DistributionInfoProvider(Processor):
    """Provide metadata of packages from their 'Distribution' file.

    A Distribution file does not have to carry every element. The
    'title' and 'os-version' elements are both optional, so this
    processor sets those output variables only when it finds them. A
    recipe must not assume they exist. Amazon Corretto is one product
    that ships no 'os-version' element.
    """

    description = __doc__
    input_variables = {
        "unpacked_path": {
            "required": True,
            "description": (
                "The path of the expanded package. "
                "Should match destination_path of "
                "FlatPkgUnpacker processor."
            ),
        },
    }
    output_variables = {
        "title": {"description": "Title of the package. Omitted if not found."},
        "min_os_version": {
            "description": (
                "Minimum supported OS version. Omitted if not found. "
                "Feed this to MunkiPkginfoMerger as the pkginfo key "
                "'minimum_os_version', which is the name Munki reads."
            )
        },
        "product_version": {"description": "The version of the product being installed"},
    }

    @staticmethod
    def find_attribute(
        distribution: ET.ElementTree, xpath: str, attribute: str
    ) -> str | None:
        """Return an attribute of the first matching element.

        :param distribution: The parsed Distribution file.
        :param xpath: XPath of the element to look for.
        :param attribute: Name of the attribute to read.
        :return: The attribute value, or None if the element is absent.
        """
        element = distribution.find(xpath)
        if element is None:
            return None
        return element.get(attribute)

    def main(self) -> None:
        """Parse the Distribution file and set the output variables.

        :raises ProcessorError: If the Distribution file cannot be read
            or parsed, or if it declares no product version.
        """
        distribution_path = os.path.join(self.env["unpacked_path"], "Distribution")
        self.output(f"Distribution file: {distribution_path}", 3)

        try:
            distribution = ET.parse(distribution_path)
        except OSError as error:
            raise ProcessorError(f"Cannot read Distribution file: {error}") from error
        except ET.ParseError as error:
            raise ProcessorError(f"Cannot parse Distribution file: {error}") from error

        product_version = self.find_attribute(
            distribution, ".//product[@version]", "version"
        )
        if product_version is None:
            raise ProcessorError(f"No product version in {distribution_path}")
        self.env["product_version"] = product_version
        self.output(f"product_version: {product_version}", 2)

        optional = {
            "title": distribution.findtext(".//title"),
            "min_os_version": self.find_attribute(
                distribution, ".//os-version[@min]", "min"
            ),
        }
        for name, value in optional.items():
            if value is None:
                self.output(f"No {name} in {distribution_path}", 2)
                continue
            self.env[name] = value
            self.output(f"{name}: {value}", 2)


if __name__ == "__main__":
    PROCESSOR = DistributionInfoProvider()
    PROCESSOR.execute_shell()
