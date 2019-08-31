#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
""""Information provider using the Distribution file of product bundles"""

from __future__ import absolute_import
import xml.etree.ElementTree as ET
from autopkglib import Processor

__all__ = ["DistributionInfoProvider"]


class DistributionInfoProvider(Processor):
    ("Provides metadata of packages from their 'Distribution' file that may "
     "be useful to other processors.")
    description = __doc__
    input_variables = {
        "unpacked_path": {
            "required": True,
            "description": ("The path of the expanded package. "
                            "Should match destination_path of "
                            "FlatPkgUnpacker processor."),
        },
    }
    output_variables = {
        "title": {
            "description": ("Title of the package")
        },
        "min_os_version": {
            "description": "Minimum supported OS version"
        },
        "product_version": {
            "description": ("The version of the product being installed")
        },
    }

    def main(self):
        distribution_path = "{}/{}".format(self.env['unpacked_path'],
                                           "Distribution")
        self.output("Distribution file: {distribution_path}".format(
            distribution_path=distribution_path),
                    3)
        distribution = ET.parse(distribution_path)
        title_xpath = './/title'
        title = distribution.find(title_xpath).text
        os_version_min_xpath = './/os-version[@min]'
        os_version_min = distribution.find(os_version_min_xpath).attrib['min']
        product_version_xpath = './/product'
        product_version = distribution.find(product_version_xpath).attrib['version']
        self.env['title'] = title
        self.env['os_version_min'] = os_version_min
        self.env['product_version'] = product_version

if __name__ == "__main__":
    PROCESSOR = DistributionInfoProvider()
    PROCESSOR.execute_shell()
