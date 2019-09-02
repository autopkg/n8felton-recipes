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
"""Provides information about the latest version of a given Ruby gem"""

from __future__ import absolute_import

import re
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["RubyGemInfoProvider"]


class RubyGemInfoProvider(Processor):
    """Provides information about the latest version of a given Ruby gem"""
    description = __doc__
    input_variables = {
        "gem_name": {
            "required": True,
            "description":
                "The name of the ruby gem you want the information for."
        },
    }
    output_variables = {
        "gem_description": {
            "description": "Short description of the gem."
        },
        "gem_version": {
            "description": "The latest version of the gem."
        },
    }

    def __init__(self):
        super(RubyGemInfoProvider, self).__init__()
        self.gem = None

    def gem_details(self, gem_name):
        search_name = '^{}$'.format(gem_name)
        gem = ['/usr/bin/gem',
               'search',
               search_name,
               '--details']
        proc = subprocess.Popen(gem,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (gem_details, e) = proc.communicate()
        if e:
            raise ProcessorError(e)
        self.gem = gem_details.strip()

    def gem_description(self):
        gem = self.gem
        return gem.split('\n')[-1].strip()

    def gem_version(self):
        version_re = (r'(?P<version>(?:(?P<major>\d+)\.)?(?:(?P<minor>\d+)\.)?'
                      r'(?P<patch>\d+))')
        gem = self.gem
        gem_version = re.search(version_re, gem)
        return gem_version.group('version')

    def main(self):
        gem_name = self.env['gem_name']
        self.gem_details(gem_name)
        self.env['gem_description'] = self.gem_description()
        self.env['gem_version'] = self.gem_version()

if __name__ == "__main__":
    PROCESSOR = RubyGemInfoProvider()
    PROCESSOR.execute_shell()
