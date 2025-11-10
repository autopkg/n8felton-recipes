#!/usr/local/autopkg/python
#
# Copyright 2025 Nathan Felton (n8felton)
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
"""Generic processor to parse JSON into usable autopkg variables."""

import json

from autopkglib import URLGetter

__all__ = ["JSONURLGetter"]


class JSONURLGetter(URLGetter):
    """Parse JSON into usable autopkg variables."""

    description = __doc__
    input_variables = {
        "url": {"required": True, "description": "Full URL to the JSON file"},
        "keys": {
            "required": True,
            "description": "The keys you wish to parse the values from the JSON source",
        },
    }
    output_variables = {}

    def get_json(self, json_url):
        """Returns the JSON file at the given URL."""
        response = self.download(json_url)
        releases = json.loads(response)
        return releases

    def main(self):
        json_response = self.get_json(self.env.get("url"))
        for k in self.env.get("keys"):
            if k in json_response:
                self.env[k] = json_response[k]


if __name__ == "__main__":
    PROCESSOR = JSONURLGetter()
    PROCESSOR.execute_shell()
