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
from typing import Any

from autopkglib import ProcessorError, URLGetter, get_autopkg_version

__all__ = ["JSONURLGetter"]


class JSONURLGetter(URLGetter):
    """Parse JSON into usable autopkg variables.

    ``keys`` accepts two forms:

    List form (existing behavior, backward-compatible):
        A list of top-level key names.  Each key is looked up directly in the
        parsed JSON object and assigned to an env var of the same name.
        Example: ``["url", "version"]``

    Dict form (new):
        A dict mapping output variable names to dotted path expressions.
        Dot-separated tokens walk the structure: integer-like tokens index
        lists, string tokens index dicts.
        Example: ``{"version": "0", "file": "2.mac_universal.link"}``
    """

    description = __doc__
    input_variables = {
        "url": {"required": True, "description": "Full URL to the JSON file"},
        "keys": {
            "required": True,
            "description": (
                "Keys to extract. List form: top-level object keys assigned to "
                "same-name env vars. Dict form: {output_var: dotted.path.expression} "
                "where integer tokens index lists and string tokens index dicts."
            ),
        },
    }
    output_variables = {}

    def get_json(self, json_url: str) -> Any:
        """Return parsed JSON from *json_url*."""
        headers = {
            "Accept": "application/json",
            "User-Agent": f"AutoPkg/{get_autopkg_version()}",
        }
        response = self.download(json_url, headers=headers)
        self.output(response, 4)
        return json.loads(response)

    def _resolve_path(self, data: Any, path: str) -> Any:
        """Walk *data* using a dotted *path* and return the value.

        :param data: Parsed JSON structure (list or dict at the root).
        :param path: Dot-separated tokens; integer-like tokens index lists,
            string tokens index dicts.
        :return: The value at the resolved path.
        :raises ProcessorError: If any token cannot be applied to the current
            node (wrong type, missing key, out-of-range index).
        """
        node = data
        for token in path.split("."):
            if token.isdigit():
                idx = int(token)
                if not isinstance(node, list):
                    raise ProcessorError(
                        f"JSONURLGetter: path token '{token}' is an index but "
                        f"current node is {type(node).__name__}, not a list."
                    )
                if idx >= len(node):
                    raise ProcessorError(
                        f"JSONURLGetter: index {idx} is out of range "
                        f"(list length {len(node)})."
                    )
                node = node[idx]
            else:
                if not isinstance(node, dict):
                    raise ProcessorError(
                        f"JSONURLGetter: path token '{token}' is a key but "
                        f"current node is {type(node).__name__}, not a dict."
                    )
                if token not in node:
                    raise ProcessorError(
                        f"JSONURLGetter: key '{token}' not found. "
                        f"Available keys: {', '.join(str(k) for k in node.keys())}"
                    )
                node = node[token]
        return node

    def main(self) -> None:
        """Fetch JSON and populate env vars from the requested keys."""
        json_response = self.get_json(self.env.get("url"))
        keys = self.env.get("keys")

        if isinstance(keys, dict):
            # Dict form: {output_var: dotted-path}
            for output_var, path in keys.items():
                self.env[output_var] = self._resolve_path(json_response, path)
        else:
            # List form: plain key names against a top-level object (original behavior)
            for k in keys:
                if k in json_response:
                    self.env[k] = json_response[k]


if __name__ == "__main__":
    PROCESSOR = JSONURLGetter()
    PROCESSOR.execute_shell()
