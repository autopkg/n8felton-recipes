#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Nathan Felton (n8felton)
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
"""Shared processor to allow recipes to download SourceForge projects
   "Best Release".
"""

import urllib2
import json

from autopkglib import Processor, ProcessorError

__all__ = ["SourceForgeBestReleaseURLProvider"]

BEST_RELEASE_API_URL = 'https://sourceforge.net/projects/{0}/best_release.json'


class SourceForgeBestReleaseURLProvider(Processor):
    """Provides URLs to the "Best Release" of a project found on SourceForge.
       The "Best Release" is set by the project maintainer, and while one would
       think that should always be the "latest stable" release, that is not
       always the case. Always verify output.
    """
    description = __doc__
    input_variables = {
        "SOURCEFORGE_PROJECT_NAME": {
            "required": True,
            "description": "A SourceForge project's \"URL Name\" \
                            e.g. https://sourceforge.net/projects/burn-osx/ \
                            would use \"URL Name\" 'burn-osx'"
        },
    }
    output_variables = {
        "url": {
            "description": "The full url for the file you want to download."
        },
        "md5checksum": {
            "description": "The MD5 checksum of the file, provided by the API."
        },
    }

    @classmethod
    def get_project_best_release(cls, project_url):
        """Returns the JSON response using the SourceForge Release API"""
        try:
            request = urllib2.Request(project_url)
            response = urllib2.urlopen(request)
        except BaseException as e:
            raise ProcessorError("Can't open %s: %s" % (project_url, e))

        releases = json.loads(response.read())
        return releases

    def main(self):
        project_url = BEST_RELEASE_API_URL.format(
            self.env['SOURCEFORGE_PROJECT_NAME'])
        self.output("Project URL: {project_url}".format(
            project_url=project_url),
                    2)
        releases = self.get_project_best_release(project_url)
        self.output(releases, 3)
        self.env['url'] = releases['platform_releases']['mac']['url']
        self.env['md5checksum'] = (releases['platform_releases']['mac']
                                   ['md5sum'])

if __name__ == "__main__":
    PROCESSOR = SourceForgeBestReleaseURLProvider()
    PROCESSOR.execute_shell()
