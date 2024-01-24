#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Nathan Felton (n8felton)
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
"""Base64 encode a given input to printable ASCII characters as specified in RFC 4648"""

import base64

from autopkglib import Processor

__all__ = ["Base64Encoder"]


class Base64Encoder(Processor):
    """Base64 encode a given input to printable ASCII characters"""

    description = __doc__
    input_variables = {
        "input": {
            "required": True,
            "description": "The input to be Base64 encoded.",
        },
    }
    output_variables = {
        "base64": {"description": "Base64 encoding of the input."},
    }

    def main(self):
        self.env["base64"] = base64.b64encode(
            self.env.get("input").encode("ascii")
        ).decode("ascii")


if __name__ == "__main__":
    PROCESSOR = Base64Encoder()
    PROCESSOR.execute_shell()
