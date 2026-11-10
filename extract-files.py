#!/usr/bin/env python3
#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#
"""Extract the stock OnePlus 7 Pro camera blobs.

The source is a full OxygenOS 12.1 dump. The camera and camera service live in
the my_product euclid image, the gallery in the my_bigball reserve image and the
extension library in system_ext. extract-utils reads the flat dump layout, so
the two euclid images have to be mounted or expanded into the dump first.

Run from the ROM root:
    ./vendor/oplus/camera-guacamole/extract-files.py <dump>

The blobs are listed in proprietary-files.txt, which is the single source of
truth for what this repository ships.
"""

import os
import sys
from pathlib import Path

# Resolve imports from the script location, including when called at ROM root.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools/extract-utils'))

from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

from extract_utils.utils import remove_dir_contents
from extract_utils.fixups_blob import blob_fixup


class PortModule(ExtractUtilsModule):
    """Refresh blobs while preserving this port's handwritten build files."""

    def cleanup(self):
        # The upstream cleanup deletes vendor_path, including this script,
        # configs, policy, tuning and (for Dolby) the control app sources.
        for proprietary_file in self.proprietary_files:
            blob_path = self.proprietary_file_vendor_path(proprietary_file)
            os.makedirs(blob_path, exist_ok=True)
            remove_dir_contents(blob_path)

    def write_makefiles(self, legacy, extract_factory):
        # Android.bp and the product .mk contain port-specific module names,
        # signing, init/VINTF wiring and configuration; keep them intact.
        pass


blob_fixups = {
    'system_ext/priv-app/OnePlusCamera/OnePlusCamera.apk':
        blob_fixup().apktool_patch('patches-camera'),
}

namespace_imports = [
    'hardware/oplus-guacamole',
    'vendor/oplus/camera-guacamole',
]

module = PortModule(
    'camera-guacamole',
    'oplus',
    device_rel_path='vendor/oplus/camera-guacamole',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
