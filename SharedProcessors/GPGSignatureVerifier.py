#!/usr/local/autopkg/python
#
# Copyright 2020 Gerard Kok
# Copyright 2026 Nathan Felton (n8felton)
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

"""Verifies a GPG signature for a downloaded file."""

import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["GPGSignatureVerifier"]


class GPGSignatureVerifier(Processor):
    """Verifies a GPG signature for a downloaded file."""

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
        "FAIL_IF_GPG_MISSING": {
            "required": False,
            "default": True,
            "description": "Raise an error if the gpg binary is not found. Set to false to skip verification when gpg is not installed.",
        },
    }
    output_variables = {"pathname": {"description": "path to the distribution file."}}

    def gpg_found(self) -> bool:
        try:
            subprocess.run(
                [self.env["gpg_path"], "--version"],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            return False
        except OSError as err:
            raise ProcessorError("Finding gpg executable failed") from err
        return True

    def import_key(self) -> None:
        gpg_import_cmd = [
            self.env["gpg_path"],
            "--keyserver",
            self.env["keyserver"],
            "--recv-keys",
            self.env["public_key_id"],
        ]
        try:
            subprocess.run(gpg_import_cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as err:
            raise ProcessorError(
                f"Importing public key failed: {err.stderr}"
            ) from err
        except OSError as err:
            raise ProcessorError(f"Importing public key failed: {err}") from err

    def verify(self) -> None:
        gpg_verify_cmd = [
            self.env["gpg_path"],
            "--verify",
            self.env["signature_file"],
            self.env["distribution_file"],
        ]
        try:
            subprocess.run(gpg_verify_cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as err:
            raise ProcessorError(
                f"Verifying signature failed: {err.stderr}"
            ) from err
        except OSError as err:
            raise ProcessorError(f"Verifying signature failed: {err}") from err

    def main(self) -> None:
        self.env["pathname"] = self.env["distribution_file"]
        if not self.gpg_found():
            if self.env.get("FAIL_IF_GPG_MISSING", True):
                raise ProcessorError(
                    "[FAIL] gpg executable not found. Install GPG to verify signatures."
                )
            self.output(
                f"[FAIL] gpg executable not found, skipping signature verification for "
                f"{self.env['distribution_file']}"
            )
            return
        self.import_key()
        self.verify()
        self.output(f"[PASS] Good signature for {self.env['distribution_file']}")


if __name__ == "__main__":
    PROCESSOR = GPGSignatureVerifier()
    PROCESSOR.execute_shell()
