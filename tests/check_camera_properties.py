#!/usr/bin/env python3
"""Resolve camera product properties against the assembled SELinux contexts.

Pass --extra-contexts for a proposed change before rebuilding the images.
This detects silently rejected/default-labeled settings; it does not replace
policy compilation or a device-side getprop check after flashing.
"""
import argparse
from pathlib import Path
import re

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--product-out', required=True, type=Path)
p.add_argument('--extra-contexts', action='append', default=[], type=Path)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
# A workspace copy can be used to validate a proposed change too.
p2 = root / 'opluscamera.mk'
if not p2.exists():
    p.error('Place this script in the camera repository tests directory')
props = []
active = False
for line in p2.read_text().splitlines():
    if re.match(r'^PRODUCT_VENDOR_PROPERTIES\s*\+=' , line):
        active = True
        line = line.split('+=', 1)[1]
    if active:
        item = line.strip().rstrip('\\').strip()
        if item and not item.startswith('#'):
            props.append(item.split('=', 1)[0])
        active = line.rstrip().endswith('\\')
paths = [a.product_out / rel for rel in (
    'system/etc/selinux/plat_property_contexts',
    'system/system_ext/etc/selinux/system_ext_property_contexts',
    'system/product/etc/selinux/product_property_contexts',
    'vendor/etc/selinux/vendor_property_contexts',
    'vendor/odm/etc/selinux/odm_property_contexts',
)] + a.extra_contexts
rules = []
for path in paths:
    for line in path.read_text().splitlines():
        fields = line.split('#', 1)[0].split()
        if fields:
            rules.append((fields[0], fields[1].split(':')[2],
                          len(fields) > 2 and fields[2] == 'exact'))
failed = []
for prop in props:
    matches = [(exact, len(name), typ) for name, typ, exact in rules
               if name == prop or (not exact and (name == '*' or prop.startswith(name)))]
    typ = max(matches)[2] if matches else '<missing>'
    print(f'{prop}: {typ}')
    if typ in {'default_prop', 'vendor_default_prop', '<missing>'}:
        failed.append(prop)
if failed:
    raise SystemExit('FAIL: settings without specific property labels: ' + ', '.join(failed))
print(f'PASS: {len(props)} vendor camera settings have specific labels')
