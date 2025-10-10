#!/usr/local/autopkg/python
#
# Copyright 2020 Nathan Felton (n8felton)
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
"""Percent-encodes a URI to be compatible with RFC 3986."""

from autopkglib import Processor, ProcessorError, URLGetter

try:
    from urllib.parse import quote  # For Python 3
except ImportError:
    from urllib2 import quote  # For Python 2

__all__ = ["URIEncoder"]


class URIEncoder(URLGetter):
    """Percent-encodes a URI to be compatible with RFC 3986."""

    description = __doc__
    input_variables = {
        "url": {"required": True, "description": "The URL/URI to percent-encode.",},
    }
    output_variables = {
        "url": {"description": "The encoded URL/URL.",},
    }

    def main(self):
        """Percent-encodes a URI to be compatible with RFC 3986."""

        self.env["url"] = quote(self.env["url"], safe=":/")


if __name__ == "__main__":
    PROCESSOR = URIEncoder()
    PROCESSOR.execute_shell()
