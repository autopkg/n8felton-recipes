#!/usr/local/autopkg/python
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
"""Release information provider for UCSF ChimeraX."""

import json
import re

from autopkglib import ProcessorError, URLGetter

__all__ = ["ChimeraInfoProvider"]

CHIMERAX_BASE_URL = "https://www.cgl.ucsf.edu"
RELEASE_INFO_BASE_URL = (
    f"{CHIMERAX_BASE_URL}/chimerax/data/release-info"
)
INSTALLER_BASE = (
    f"{CHIMERAX_BASE_URL}/chimerax/cgi-bin/secure/chimerax-get.py"
)

VALID_RELEASE_TYPES = ("production", "candidate", "daily")
VALID_PLATFORMS = ("mac_universal", "mac_arm64", "macosx")


class ChimeraInfoProvider(URLGetter):
    """Provides version and download URL for UCSF ChimeraX from the
    production, candidate, or daily release JSON."""

    description = __doc__
    input_variables = {
        "release_type": {
            "required": False,
            "default": "production",
            "description": (
                "Which release channel to download. "
                f"One of: {', '.join(VALID_RELEASE_TYPES)}."
            ),
        },
        "platform": {
            "required": False,
            "default": "mac_universal",
            "description": (
                "macOS platform variant to download. "
                f"One of: {', '.join(VALID_PLATFORMS)}. "
                "mac_universal supports both Apple Silicon and Intel; "
                "mac_arm64 is Apple Silicon only; "
                "macosx is Intel only."
            ),
        },
    }
    output_variables = {
        "version": {"description": "The version of ChimeraX."},
        "url": {"description": "The download URL for the ChimeraX installer."},
    }

    def get_release_info(self, url):
        """Fetch and return parsed release JSON."""
        response = self.download(url).decode("utf-8")
        return json.loads(response)

    def resolve_download_url(self, link):
        """Follow the ChimeraX license CGI flow to get the direct download URL.

        The CGI requires two steps:
        1. GET ?file=<link>&choice=Accept  → HTML page with meta-refresh to ?ident=...&choice=Notified
        2. GET ?ident=<token>&...&choice=Notified → application/octet-stream
        """
        accept_url = f"{INSTALLER_BASE}?file={link}&choice=Accept"
        self.output(f"Accepting license at: {accept_url}", 2)
        accept_html = self.download(accept_url).decode("utf-8")

        match = re.search(r'content="\d+;url=([^"]+)"', accept_html)
        if not match:
            raise ProcessorError(
                "Could not find meta-refresh redirect in ChimeraX license page."
            )

        notified_path = match.group(1)
        # Path is server-relative (starts with /)
        if notified_path.startswith("/"):
            notified_url = f"{CHIMERAX_BASE_URL}{notified_path}"
        else:
            notified_url = notified_path

        self.output(f"Resolved download URL: {notified_url}", 2)
        return notified_url

    def main(self):
        release_type = self.env.get("release_type", "production")
        platform = self.env.get("platform", "mac_universal")

        if release_type not in VALID_RELEASE_TYPES:
            raise ProcessorError(
                f"Invalid release_type '{release_type}'. "
                f"Must be one of: {', '.join(VALID_RELEASE_TYPES)}"
            )

        if platform not in VALID_PLATFORMS:
            raise ProcessorError(
                f"Invalid platform '{platform}'. "
                f"Must be one of: {', '.join(VALID_PLATFORMS)}"
            )

        release_info_url = f"{RELEASE_INFO_BASE_URL}/{release_type}.json"
        self.output(f"Release type: {release_type}")
        release_data = self.get_release_info(release_info_url)
        self.output(f"Raw release data: {release_data}", 4)

        # JSON structure: [version, date, {platform_key: {link, version, md5, sha256, ...}}]
        if not isinstance(release_data, list) or len(release_data) < 3:
            raise ProcessorError(
                f"Unexpected JSON structure from {release_info_url}. "
                "Expected a list of at least 3 elements."
            )

        version = release_data[0]
        platforms = release_data[2]

        if platform not in platforms:
            raise ProcessorError(
                f"Platform '{platform}' not found in release info. "
                f"Available: {', '.join(platforms.keys())}"
            )

        info = platforms[platform]
        if "link" not in info:
            raise ProcessorError(
                f"Platform '{platform}' is missing required 'link' field in release info."
            )

        url = self.resolve_download_url(info["link"])

        self.env["version"] = version
        self.env["url"] = url

        self.output(f"Version: {version}")
        self.output(f"Platform: {platform}")


if __name__ == "__main__":
    PROCESSOR = ChimeraInfoProvider()
    PROCESSOR.execute_shell()
