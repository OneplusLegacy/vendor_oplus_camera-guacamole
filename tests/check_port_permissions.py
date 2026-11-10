#!/usr/bin/env python3
"""Check the consumed APK, privileged allowlist and preserved OEM component guards."""
from pathlib import Path
import argparse
import re
import subprocess
import xml.etree.ElementTree as E
p=argparse.ArgumentParser();p.add_argument('--rom-root',required=True,type=Path);p.add_argument('--camera-apk',type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[1];tool=a.rom_root/'out/host/linux-x86/bin/aapt2'
camera=a.camera_apk or root/'proprietary/system_ext/priv-app/OnePlusCamera/OnePlusCamera.apk'
gallery=root/'proprietary/system_ext/priv-app/OnePlusGallery/OnePlusGallery.apk'
ns='{http://schemas.android.com/apk/res/android}'
requested=subprocess.check_output([str(tool),'dump','permissions',str(camera)],text=True)
assert "name='android.permission.SYSTEM_CAMERA'" in requested, 'Camera APK did not receive the manifest patch'
allowed=E.parse(root/'configs/permissions/privapp-permissions-oneplus-camera.xml').getroot()
assert any(n.get('name')=='android.permission.SYSTEM_CAMERA' for app in allowed if app.get('package')=='com.oneplus.camera' for n in app)
manifest=E.parse(root/'permissions/AndroidManifest.xml').getroot()
definitions={n.get(ns+'name') for n in manifest.findall('permission')}
assert all(n.get(ns+'protectionLevel')=='signature' for n in manifest.findall('permission'))
guards=set()
for apk in (camera,gallery):
    tree=subprocess.check_output([str(tool),'dump','xmltree',str(apk),'--file','AndroidManifest.xml'],text=True)
    guards.update(re.findall(r'android:(?:permission|readPermission|writePermission)\([^)]*\)="([^"\n]+)"',tree))
assert definitions <= guards, 'Permission definitions must be backed by actual component guards: '+str(definitions-guards)
assert 'oplus.permission.OPLUS_COMPONENT_SAFE' in definitions
assert 'com.oplus.permission.safe.SECURITY' in definitions
print('PASS requested/allowlisted SYSTEM_CAMERA and',len(definitions),'signature-only OEM component guards')
