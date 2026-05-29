#!/usr/local/autopkg/python
#
# Copyright 2015 Nathan Felton (n8felton)
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
"""Shared processor to allow recipes to download Apple support downloads."""

import re

from autopkglib import URLGetter, ProcessorError

__all__ = ["AppleSupportDownloadInfoProvider"]

APPLE_SUPPORT_URL = "https://support.apple.com"


class AppleSupportDownloadInfoProvider(URLGetter):
    """Provides links to downloads posted to the Apple support knowledge bases."""

    description = __doc__
    input_variables = {
        "ARTICLE_NUMBER": {
            "required": True,
            "description": (
                "The numeric Apple support article ID, "
                "e.g. https://support.apple.com/106384 "
                "-> ARTICLE_NUMBER = 106384"
            ),
        },
    }
    output_variables = {
        "article_url": {
            "description": "The URL for the support article related to the download."
        },
        "url": {"description": "The full url for the file you want to download."},
        "version": {"description": "The version of the support download"},
    }

    def get_download_url(self, html: str) -> str:
        """Extract the primary download URL from the support article page."""
        # The download button uses class="cta gb-call-to-action" on new-style pages
        match = re.search(r'<a[^>]+class="[^"]*cta[^"]*"[^>]+href="([^"]+)"', html)
        if match:
            url = match.group(1)
            self.output(f"Download URL: {url}", 2)
            return url
        raise ProcessorError("Unable to find download URL")

    def get_version(self, html: str) -> str:
        """Extract version from the support article page title."""
        title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        if not title_match:
            raise ProcessorError("Unable to determine version: no <title> found")
        title = title_match.group(1)
        self.output(f"Article title: {title}", 2)
        # Match date-style (e.g. 2017-001) before dotted (e.g. 5.1.5769) to avoid
        # truncating year-only from date strings
        version_match = re.search(r"(\d{4}-\d{3}|\d+(?:\.\d+){1,3})", title)
        if version_match:
            version = version_match.group(1)
            self.output(f"Version: {version}", 2)
            return version
        raise ProcessorError("Unable to determine version")

    def main(self) -> None:
        """Main process."""
        article_number = self.env["ARTICLE_NUMBER"]
        article_url = f"{APPLE_SUPPORT_URL}/{article_number}"
        self.env["article_url"] = article_url
        self.output(f"Article URL: {article_url}", 2)

        html = self.download(article_url).decode("utf-8")

        self.env["url"] = self.get_download_url(html)
        self.env["version"] = self.get_version(html)


if __name__ == "__main__":
    PROCESSOR = AppleSupportDownloadInfoProvider()
    PROCESSOR.execute_shell()
