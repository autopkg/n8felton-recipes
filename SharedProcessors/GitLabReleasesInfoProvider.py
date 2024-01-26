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
"""Shared processor to allow recipes to download releases from GitLab instances."""

import certifi
import json
import os
import re
import ssl
from pprint import pformat
from urllib.request import Request, urlopen

from autopkglib import Processor, ProcessorError, get_autopkg_version

__all__ = ["GitLabReleasesInfoProvider"]


class GitLabReleasesInfoProvider(Processor):
    """Provides the URL of a release asset of a given project in GitLab.

    Unless `link_regex` is provided, a lot of assumptions are made in an attempt to
    find the latest release. Unless you know there is typically only 1 file released,
    it is highly recommended to set `link_regex`.
    """

    description = __doc__
    input_variables = {
        "link_regex": {
            "required": False,
            "description": ("Return asset links that match this regex"),
        },
        "latest": {
            "required": False,
            "description": ("Filters results to include only the most recent release."),
        },
        "GITLAB_HOSTNAME": {
            "required": True,
            "default": "gitlab.com",
            "description": (
                "If your organization has an internal GitLab instance "
                "set this value to your internal GitLab URL."
            ),
        },
        "GITLAB_PROJECT_ID": {
            "required": True,
            "description": (
                "The ID or URL-encoded path of the project."
                "e.g. `123` or `autopkg%2Frecipes`"
            ),
        },
        "PRIVATE_TOKEN": {
            "required": False,
            "description": (
                "GitLab personal, group, or project access token."
                "MUST have the `api` scope granted."
                "Optionally set a environment variable, but is required in one or the "
                "other."
            ),
        },
    }
    output_variables = {
        "direct_asset_url": {
            "description": (
                "direct_asset_url matching the `link_regex` and/or `latest` inputs."
            )
        },
        "url": {
            "description": ("url matching the `link_regex` and/or `latest` inputs.")
        },
        "version": {
            "description": (
                "Version based on the release tag_name. (Strips `v` prefix)"
            )
        },
    }

    def ssl_context_certifi(self):
        """Provide ssl context using certifi certificate store."""
        return ssl.create_default_context(cafile=certifi.where())

    def gitlab_api_get(self, endpoint):
        """Helps to communicate with the GitLab API by setting necessary headers."""
        GITLAB_HOSTNAME = self.env.get("GITLAB_HOSTNAME")
        GITLAB_API_BASE_URL = f"https://{GITLAB_HOSTNAME}/api/v4"
        PRIVATE_TOKEN = self.env.get("PRIVATE_TOKEN")
        if not PRIVATE_TOKEN:
            raise ProcessorError(
                f"PRIVATE_TOKEN is not set as environment or input variable."
            )

        headers = {
            "PRIVATE-TOKEN": PRIVATE_TOKEN,
            "User-Agent": f"AutoPkg/{get_autopkg_version()}",
        }
        url = f"{GITLAB_API_BASE_URL}{endpoint}"
        req = Request(url, headers=headers)
        with urlopen(req, context=self.ssl_context_certifi()) as response:
            data = response.read()
        return data

    def get_releases(self, latest=False):
        """Return a list of releases for a given GitLab project."""
        project_id = self.env.get("GITLAB_PROJECT_ID")
        releases_endpoint = f"/projects/{project_id}/releases"
        if latest:
            releases_endpoint += "/permalink/latest"
        releases = self.gitlab_api_get(releases_endpoint)
        releases = [json.loads(releases)]
        self.output(pformat(releases), 3)
        return releases

    def get_release_link(self, releases, regex=None):
        """Returns the release details and the direct_asset_url as tuple"""
        if not regex:
            return releases[0], releases[0]["assets"]["links"][0]
        self.output(f"Using regex: {regex}")
        for release in releases:
            links = release["assets"]["links"]
            for link in links:
                try:
                    if re.match(regex, link["name"]):
                        self.output(f"Regex pattern: {regex}", 2)
                        self.output(f"Regex matched: {link['name']}", 2)
                        return release, link
                except re.error as e:
                    raise ProcessorError(f"Invalid regex: {regex} ({e})")

    def main(self):
        PRIVATE_TOKEN = os.getenv("PRIVATE_TOKEN") or self.env.get("PRIVATE_TOKEN")
        self.env["PRIVATE_TOKEN"] = PRIVATE_TOKEN
        releases = self.get_releases(latest=self.env.get("latest"))
        release, link = self.get_release_link(
            releases, regex=self.env.get("link_regex")
        )
        self.env["url"] = link.get("url")
        self.env["direct_asset_url"] = link.get("direct_asset_url")

        # Get the version from the tag name
        tag_name = release["tag_name"]
        # Strip any leading "v" prefix
        if tag_name.startswith("v"):
            tag_name = tag_name.lstrip("v")
        self.env["version"] = tag_name


if __name__ == "__main__":
    with open("/tmp/autopkg.plist", "r") as input:
        PROCESSOR = GitLabReleasesInfoProvider(infile=input)
        PROCESSOR.execute_shell()
