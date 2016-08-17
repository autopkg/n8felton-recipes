#!/usr/bin/python
#
# Copyright 2010 Per Olofsson
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
"""See docstring for ShortVersionStringFixer class"""

import os.path
import re
#pylint: disable=no-name-in-module
from Foundation import NSData, \
                       NSPropertyListSerialization, \
                       NSPropertyListXMLFormat_v1_0, \
                       NSPropertyListMutableContainers
#pylint: enable=no-name-in-module

from autopkglib import Processor, ProcessorError


__all__ = ["ShortVersionStringFixer"]


class ShortVersionStringFixer(Processor):
    """Fixes CFBundleShortVersionString."""
    description = __doc__
    input_variables = {
        "app_path": {
            "required": True,
            "description": "Path to .app.",
        },
        "version": {
            "required": True,
            "description": "Version of .app",
        },
    }
    output_variables = {
        "bundleid": {
            "description": "Bundle identifier of .app.",
        },
        "version": {
            "description": "Version of .app.",
        },
    }

    def format_version(self, version):
        v = ['0']*3
        version = re.sub("-", ".", version)
        for i, s in enumerate(version.split('.',2)):
            int = re.sub("[^0-9]", "", s)
            v[i] = int if int else '0'
        major = v[0]
        minor = v[1]
        build = v[2]
        version = "%s.%s.%s" % (major, minor, build)
        return version

    def read_bundle_info(self, path):
        """Read Contents/Info.plist inside a bundle."""
        #pylint: disable=no-self-use
        plistpath = os.path.join(path, "Contents", "Info.plist")
        info, _, error = (
            NSPropertyListSerialization.
            propertyListFromData_mutabilityOption_format_errorDescription_(
                NSData.dataWithContentsOfFile_(plistpath),
                NSPropertyListMutableContainers,
                None,
                None))
        if error:
            raise ProcessorError("Can't read %s: %s" % (plistpath, error))

        return info

    def write_bundle_info(self, info, path):
        """Write Contents/Info.plist inside a bundle."""
        #pylint: disable=no-self-use
        plistpath = os.path.join(path, "Contents", "Info.plist")
        plist_data, error = (
            NSPropertyListSerialization.
            dataFromPropertyList_format_errorDescription_(
                info,
                NSPropertyListXMLFormat_v1_0,
                None))
        if error:
            raise ProcessorError("Can't serialize %s: %s" % (plistpath, error))

        if not plist_data.writeToFile_atomically_(plistpath, True):
            raise ProcessorError("Can't write %s" % (plistpath))

    def main(self):
        """Perform our Processor's task"""
        app_path = self.env["app_path"]
        info = self.read_bundle_info(app_path)
        self.env["bundleid"] = info["CFBundleIdentifier"]
        self.env["version"] = self.format_version(self.env["version"])
        info["CFBundleVersion"] = self.env["version"]
        info["CFBundleShortVersionString"] = self.env["version"]
        self.write_bundle_info(info, app_path)


if __name__ == '__main__':
    PROCESSOR = ShortVersionStringFixer()
    PROCESSOR.execute_shell()
