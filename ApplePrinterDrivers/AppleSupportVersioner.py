#!/usr/env python
# -*- coding: utf-8 -*-
#
# Created by Nathan Felton (n8felton)

import re
from os import path
from autopkglib import Processor, ProcessorError

__all__ = ["AppleSupportVersioner"]


class AppleSupportVersioner(Processor):
    description = "Provides version numbers for downloads from \
                   AppleSupportDownloader"
    input_variables = {
        "path_name": {
            "required": True,
            "description": "The full path to the file downloaded."
        }
    }
    output_variables = {
        "version": {
            "description": "The version of the download based on the filename"
        }
    }

    def main(self):
        self.path_name = self.env['path_name']
        file = path.basename(self.path_name)
        regex = '(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)'
        match = re.search(regex, file)
        if match:
            self.version = match.group(0)
            self.output("Version is {version}".format(
                version=match.group(0)))

        self.env['version'] = self.version

if __name__ == "__main__":
    processor = AppleSupportVersioner()
    processor.execute_shell()
