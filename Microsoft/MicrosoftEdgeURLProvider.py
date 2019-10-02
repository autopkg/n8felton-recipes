#!/usr/bin/python
#
# Copyright 2019 Nate Felton <n8felton@gmail.com>
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
"""See docstring for MicrosoftEdgeURLProvider class"""

from autopkglib import Processor, ProcessorError

__all__ = ["MicrosoftEdgeURLProvider"]

MS_LINKID_URL = "https://go.microsoft.com/fwlink/?linkid={linkid}"
CHANNEL_LINKID = {
    # 'Stable': '',
    "Beta": 2069439,
    "Dev": 2069340,
    "Canary": 2069147,
}


class MicrosoftEdgeURLProvider(Processor):
    (
        "Provides the URL to the latest version of the selected release of "
        "Microsoft Edge"
    )
    description = __doc__
    input_variables = {
        "CHANNEL": {
            "required": False,
            "default": "Beta",
            "description": (
                "Which channel to download. "
                "Options: {}".format(CHANNEL_LINKID.keys())
            ),
        }
    }
    output_variables = {
        "url": {"description": "URL to the latest release of the given CHANNEL"},
        "CHANNEL": {"description": "The channel used for the download."}
    }

    def main(self):
        channel = self.env.get("CHANNEL") or self.input_variables["CHANNEL"]["default"]
        print(self.input_variables["CHANNEL"]["description"])
        url = MS_LINKID_URL.format(linkid=CHANNEL_LINKID[channel])
        self.env["url"] = url
        self.env["CHANNEL"] = channel


if __name__ == "__main__":
    PROCESSOR = MirosoftEdgeURLProvider()
    PROCESSOR.execute_shell()
