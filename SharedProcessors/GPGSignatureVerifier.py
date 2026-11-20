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

import os
import re
import shutil
import subprocess
import tempfile

from autopkglib import Processor, ProcessorError

__all__ = ["GPGSignatureVerifier"]

TRUE_STRINGS = ("true", "yes", "1", "on")
# v4 keys have 40-hex fingerprints and v5/v6 keys 64. Anything shorter is a key ID,
# and anyone can generate a key with the same ID.
FULL_FINGERPRINT = re.compile(r"[0-9A-F]{40}|[0-9A-F]{64}")


def normalize_key_id(value: str) -> str:
    """Uppercase hex without spaces or a 0x prefix, the form gpg's status lines use."""
    compact = "".join(value.split()).upper()
    return compact.removeprefix("0X")


class GPGSignatureVerifier(Processor):
    """Verifies a GPG signature for a downloaded file.

    The key is imported into a temporary keyring that is deleted after the check, so
    only that key can satisfy the check and ~/.gnupg is not read or changed. When
    expected_fingerprint is set, or public_key_id is a full fingerprint, the signing
    key or its primary key must also match that fingerprint.
    """

    description = __doc__
    input_variables = {
        "gpg_path": {
            "required": False,
            "description": "location of the gpg binary",
        },
        "public_key_id": {
            "required": False,
            "description": (
                "public key id to import from keyserver. Required unless "
                "public_key_file is set. A full 40- or 64-hex fingerprint also pins "
                "the signer when expected_fingerprint is not set."
            ),
        },
        "public_key_file": {
            "required": False,
            "description": (
                "local file that contains the public key, armored or binary, imported "
                "instead of fetching public_key_id from keyserver"
            ),
        },
        "expected_fingerprint": {
            "required": False,
            "description": (
                "full fingerprint (40 or 64 hex; spaces and 0x are ignored) that the "
                "signing key or its primary key must match"
            ),
        },
        "keyserver": {
            "required": False,
            "default": "hkps://keys.openpgp.org",
            "description": "key server to retrieve public key from",
        },
        "distribution_file": {"required": True, "description": "file to verify"},
        "signature_file": {"required": True, "description": "file with signature"},
        "PASS_IF_GPG_MISSING": {
            "required": False,
            "default": False,
            "description": "Skip verification if the gpg binary is not found. Set to true to allow recipes to proceed when gpg is not installed.",
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

    def expected_fingerprint(self) -> str:
        configured_value = self.env.get("expected_fingerprint") or ""
        configured = normalize_key_id(configured_value)
        if configured:
            if not FULL_FINGERPRINT.fullmatch(configured):
                raise ProcessorError(
                    f"expected_fingerprint must be 40 or 64 hex characters: {configured}"
                )
            return configured
        key_id_value = self.env.get("public_key_id") or ""
        key_id = normalize_key_id(key_id_value)
        if FULL_FINGERPRINT.fullmatch(key_id):
            return key_id
        if key_id:
            self.output(
                f"WARNING: public_key_id {key_id} is not a full fingerprint, so the "
                "signer is not pinned. Set expected_fingerprint to pin it."
            )
        return ""

    def run_gpg(
        self, homedir: str, arguments: list[str], action: str
    ) -> subprocess.CompletedProcess[str]:
        gpg_cmd = [self.env["gpg_path"], "--homedir", homedir, "--batch", *arguments]
        try:
            return subprocess.run(
                gpg_cmd,
                capture_output=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as err:
            raise ProcessorError(f"{action} failed: {err.stderr.strip()}") from err
        except OSError as err:
            raise ProcessorError(f"{action} failed: {err}") from err

    def import_key(self, homedir: str) -> None:
        if self.env.get("public_key_file"):
            import_args = ["--import", self.env["public_key_file"]]
        else:
            import_args = [
                "--keyserver",
                self.env["keyserver"],
                "--recv-keys",
                self.env["public_key_id"],
            ]
        self.run_gpg(homedir, import_args, "Importing public key")

    def verify(self, homedir: str, expected_fingerprint: str) -> None:
        verify_args = [
            "--status-fd",
            "1",
            "--verify",
            self.env["signature_file"],
            self.env["distribution_file"],
        ]
        completed = self.run_gpg(homedir, verify_args, "Verifying signature")
        # Split each "[GNUPG:] KEYWORD ..." status line into fields; drop other lines.
        status_lines = [
            line.split()
            for line in completed.stdout.splitlines()
            if line.startswith("[GNUPG:] ")
        ]
        # gpg exits 0 for a good signature by an expired or revoked key, and reports
        # those as EXPKEYSIG or REVKEYSIG, not GOODSIG. Slices such as fields[1:2]
        # return an empty list for a short line where fields[1] raises IndexError.
        if not any(fields[1:2] == ["GOODSIG"] for fields in status_lines):
            raise ProcessorError(
                "Verifying signature failed: no GOODSIG from gpg. "
                f"{completed.stderr.strip()}"
            )
        if not expected_fingerprint:
            return
        # Counting "[GNUPG:]" as field 0, VALIDSIG has the signing key's fingerprint in
        # field 2 and its primary key's fingerprint in field 11.
        signer_fingerprints: set[str] = set()
        for fields in status_lines:
            if fields[1:2] == ["VALIDSIG"]:
                signer_fingerprints.update(fields[2:3] + fields[11:12])
        if expected_fingerprint not in signer_fingerprints:
            raise ProcessorError(
                f"Verifying signature failed: signed by {sorted(signer_fingerprints)}, "
                f"expected {expected_fingerprint}. {completed.stderr.strip()}"
            )

    def remove_temp_keyring(self, homedir: str) -> None:
        # gpgconf ships beside the real gpg binary, which is often behind a symlink
        # such as /usr/local/bin/gpg -> /usr/local/MacGPG2/bin/gpg2.
        gpg_binary = shutil.which(self.env["gpg_path"]) or self.env["gpg_path"]
        gpg_real_path = os.path.realpath(gpg_binary)
        gpgconf_path = os.path.join(os.path.dirname(gpg_real_path), "gpgconf")
        if os.path.exists(gpgconf_path):
            subprocess.run(
                [gpgconf_path, "--homedir", homedir, "--kill", "all"],
                capture_output=True,
                check=False,
            )
        shutil.rmtree(homedir, ignore_errors=True)

    def main(self) -> None:
        self.env["pathname"] = self.env["distribution_file"]
        if "gpg_path" not in self.env or not self.env["gpg_path"]:
            self.env["gpg_path"] = shutil.which("gpg") or ""
        if not self.gpg_found():
            pass_if_missing = self.env.get("PASS_IF_GPG_MISSING") or False
            # A recipe plist gives a bool. -k and standalone key=value arguments give a
            # string, and any non-empty string such as "false" is truthy.
            if isinstance(pass_if_missing, str):
                pass_if_missing = pass_if_missing.strip().lower() in TRUE_STRINGS
            if not pass_if_missing:
                raise ProcessorError(
                    "[FAIL] gpg executable not found. Install GPG to verify signatures."
                )
            self.output(
                f"[FAIL] gpg executable not found, skipping signature verification for "
                f"{self.env['distribution_file']}"
            )
            return
        if not self.env.get("public_key_file") and not self.env.get("public_key_id"):
            raise ProcessorError("Set public_key_id or public_key_file.")
        expected_fingerprint = self.expected_fingerprint()
        # A short path keeps gpg-agent's and dirmngr's sockets inside macOS's
        # 104-byte socket path limit; mkdtemp creates the folder 0700.
        homedir = tempfile.mkdtemp(prefix="gpg.")
        try:
            self.import_key(homedir)
            self.verify(homedir, expected_fingerprint)
        finally:
            self.remove_temp_keyring(homedir)
        # Name the signer only when one was pinned.
        pinned = f", signer {expected_fingerprint}" if expected_fingerprint else ""
        self.output(
            f"[PASS] Good signature for {self.env['distribution_file']}{pinned}"
        )


if __name__ == "__main__":
    PROCESSOR = GPGSignatureVerifier()
    PROCESSOR.execute_shell()
