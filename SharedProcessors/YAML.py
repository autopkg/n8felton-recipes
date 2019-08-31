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
"""Generic processor to parse YAML into usable autopkg variables"""

from __future__ import absolute_import
import urllib2
import yaml

from autopkglib import Processor, ProcessorError

__all__ = ["YAML"]


class YAML(Processor):
    """Parse YAML into usable autopkg variables"""
    description = __doc__
    input_variables = {
        "url": {
            "required": True,
            "description": "Full URL to the YAML file"
        },
        "keys": {
            "required": True,
            "description":
                "The keys you wish to parse the values from the YAML source"
        }
    }

    @classmethod
    def get_yaml(cls, yaml_url):
        """Returns the YAML file at the given URL"""
        try:
            request = urllib2.Request(yaml_url)
            response = urllib2.urlopen(request)
        except BaseException as e:
            raise ProcessorError("Can't open %s: %s" % (yaml_url, e))

        releases = yaml.load(response.read())
        return releases

    def main(self):
        yaml_response = self.get_yaml(self.env.get('url'))
        for k in self.env.get('keys'):
            if k in yaml_response:
                self.env[k] = yaml_response[k]

if __name__ == "__main__":
    PROCESSOR = YAML()
    PROCESSOR.execute_shell()
