#!/usr/local/autopkg/python
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
"""Generic processor to parse YAML into usable autopkg variables."""

import yaml

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["YAML"]


class YAML(URLGetter):
    """Parse YAML into usable autopkg variables."""

    description = __doc__
    input_variables = {
        "url": {"required": True, "description": "Full URL to the YAML file"},
        "keys": {
            "required": True,
            "description": "The keys you wish to parse the values from the YAML source",
        },
    }
    output_variables = {}

    def get_yaml(self, yaml_url):
        """Returns the YAML file at the given URL."""
        response = self.download(yaml_url)
        releases = yaml.load(response)
        return releases

    def main(self):
        yaml_response = self.get_yaml(self.env.get("url"))
        for k in self.env.get("keys"):
            if k in yaml_response:
                self.env[k] = yaml_response[k]


if __name__ == "__main__":
    PROCESSOR = YAML()
    PROCESSOR.execute_shell()
