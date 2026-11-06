#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils:../../../hardware/oplus-guacamole/extract-utils-ext python3
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
    ./vendor/oplus/camera-guacamole/extract-files.py <dump> --section all

The blobs are listed in proprietary-files.txt, which is the single source of
truth for what this repository ships.
"""

from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/oplus-guacamole',
    'vendor/oplus/camera-guacamole',
]

module = ExtractUtilsModule(
    'camera',
    'oplus/camera-guacamole',
    device_rel_path='vendor/oplus/camera-guacamole',
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(module, 'vendor/oplus/camera-guacamole')
    utils.run()
