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
""""Changes the version of a flat package by modifying it's PackageInfo"""

import xml.etree.ElementTree as ET
from autopkglib import Processor, ProcessorError

__all__ = ["PkgInfoVersioner"]


class PkgInfoVersioner(Processor):
    ("Finds a package given it's package ID and modifies the PackageInfo "
     "version, resulting in the receipt database containing the modified "
     "version information.")
    description = __doc__
    input_variables = {
        "unpacked_path": {
            "required": True,
            "description": ("The path where the package containing the "
                            "PKGID you want to change the version of is "
                            "extracted to. Should match destination_path of "
                            "FlatPkgUnpacker processor."),
        },
        "PKGID": {
            "required": True,
            "description": ("The package id of the pkg-ref you want to change"
                            "the version of."),
        },
        "VERSION": {
            "required": True,
            "description": "The version you want to set the PKGID to",
        },
    }
    output_variables = {
    }

    def main(self):
        distribution_path = "{}/{}".format(self.env['unpacked_path'],
                                           "Distribution")
        self.output("Distribution file: {distribution_path}".format(
            distribution_path=distribution_path),
                    3)
        distribution = ET.parse(distribution_path)
        pkg_ref_xpath = './/pkg-ref[@id="{}"][@version]'.format(
            self.env['PKGID'])
        pkg = getattr(distribution.find(pkg_ref_xpath), 'text', None)
        if pkg is None:
            raise ProcessorError("PKGID was not found.")
        pkg_path = pkg.lstrip('#')
        self.output("Package file: {pkg_path}".format(
            pkg_path=pkg_path),
                    3)
        packageinfo_path = "{}/{}/{}".format(self.env['unpacked_path'],
                                             pkg_path,
                                             "PackageInfo")
        self.output("PackageInfo file: {packageinfo_path}".format(
            packageinfo_path=packageinfo_path),
                    3)
        packageinfo = ET.parse(packageinfo_path)
        packageinfo_xpath = '[@identifier="{}"]'.format(self.env['PKGID'])
        packageinfo.find(packageinfo_xpath).set('version', self.env['VERSION'])
        packageinfo.write(packageinfo_path)

if __name__ == "__main__":
    PROCESSOR = PkgInfoVersioner()
    PROCESSOR.execute_shell()
