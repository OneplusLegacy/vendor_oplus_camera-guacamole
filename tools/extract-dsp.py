#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Extract a pinned Hexagon image from the stock APK for prebuilt_rfsa."""
import hashlib
from pathlib import Path
import sys
import zipfile


def main():
    apk, member, output, expected = sys.argv[1:]
    with zipfile.ZipFile(apk) as archive:
        data = archive.read(member)
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('Stock camera DSP image hash mismatch: ' + member)
    if data[:4] != b'\x7fELF' or int.from_bytes(data[18:20], 'little') != 164:
        raise SystemExit('Expected Qualcomm Hexagon ELF: ' + member)
    Path(output).write_bytes(data)


if __name__ == '__main__':
    main()
