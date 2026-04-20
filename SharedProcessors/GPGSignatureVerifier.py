#!/usr/local/autopkg/python
#
# Copyright 2020 Gerard Kok
# Copyright 2026 Nathan Felton
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

# pylint: disable=import-error, invalid-name

"""See docstring for GPGSignatureVerifier class"""

from __future__ import absolute_import

import errno
import os
import re
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["GPGSignatureVerifier"]


def check_for_goodsig(string):
    """Checks for GOODSIG"""
    return re.search(r"^\[GNUPG:\] GOODSIG ([0-9A-F]{8,})", string, re.M)


class GPGSignatureVerifier(Processor):
    """Verifies a gpg signature. Succeeds if gpg is not installed,
    or if the signature is good. Fails otherwise."""

    description = __doc__
    input_variables = {
        "gpg_path": {
            "required": False,
            "default": "/usr/local/bin/gpg",
            "description": "location of the gpg binary",
        },
        "public_key_id": {"required": True, "description": "public key id to import"},
        "keyserver": {
            "required": False,
            "default": "hkps://keys.openpgp.org",
            "description": "key server to retrieve public key from",
        },
        "distribution_file": {"required": True, "description": "file to verify"},
        "signature_file": {"required": True, "description": "file with signature"},
    }
    output_variables = {"pathname": {"description": "path to the distribution file."}}

    def gpg_found(self):
        """If GPG executable found, get key"""
        gpg_version_cmd = [self.env["gpg_path"], "--version"]
        try:
            with open(os.devnull, "w") as devnull:
                subprocess.call(gpg_version_cmd, stdout=devnull, stderr=devnull)
        except OSError as err_msg:
            if err_msg.errno == errno.ENOENT:
                return False
            else:
                raise ProcessorError("Finding gpg executable failed")
        return True

    def import_key(self):
        """Import Key"""
        gpg_import_cmd = [
            self.env["gpg_path"],
            "--keyserver",
            self.env["keyserver"],
            "--recv-keys",
            self.env["public_key_id"],
        ]
        try:
            with open(os.devnull, "w") as devnull:
                subprocess.call(gpg_import_cmd, stdout=devnull, stderr=devnull)
        except OSError:
            raise ProcessorError("Importing public key failed")

    def verify(self):
        """Verify"""
        gpg_verify_cmd = [
            self.env["gpg_path"],
            "--status-fd",
            "1",
            "--verify",
            self.env["signature_file"],
            self.env["distribution_file"],
        ]
        try:
            proc = subprocess.Popen(
                gpg_verify_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            (output, _) = proc.communicate()
            if proc.returncode:
                raise ProcessorError("Verifying signature failed")
            return check_for_goodsig(output.decode("utf-8"))
        except:
            raise ProcessorError("Verifying signature failed")

    def main(self):
        """Gimme some main"""
        self.env["pathname"] = self.env["distribution_file"]
        if self.gpg_found():
            self.import_key()
            if self.verify():
                self.output("Good signature for %s" % self.env["distribution_file"])
            else:
                raise ProcessorError("Bad signature")
        else:
            self.output(
                "gpg executable not found, therefore assuming signature "
                "for %s is good" % self.env["distribution_file"]
            )


if __name__ == "__main__":
    PROCESSOR = GPGSignatureVerifier()
    PROCESSOR.execute_shell()
