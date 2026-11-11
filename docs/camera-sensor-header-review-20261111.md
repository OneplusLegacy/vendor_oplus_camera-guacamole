# Qualcomm sensor table header selection (2026-11-11)

A direct camera-characteristics query from the camera UID returns
org.quic.camera2.sensormode.info.SensorModeTable as
[10,3,4000,3000,30,4000,3000,30,4000,3000,60,2000,1128,240,1296,736,480,
2000,1500,120,4000,3000,23,4000,3000,30,8000,6000,28,4000,3000,30].
The first two entries are row count and stride, followed by ten triplets.

The original APK reads stride from [1], but both IntRange scans start at zero.
They compare the wrong columns and leave the selected mode at -1. Its existing
index calculation (offset-2)/stride+1 already expects a two-integer header.
Start both searches at offset two without replacing the actual sensor table,
forcing a mode, changing FPS or removing optional features. Original and current
pre-fix OPNormalCamcorderImpl disassembly are identical.

The diagnostic update with this correction selects mode 1 and logs delivery of
0x18116 for 4K30. Video STILL exits with HAL configureStreams -38. This repairs
selection, not the complete recording failure. The framework setter patch and
the CameraService cameraMDM identity hook/policy must also be present in the
next ROM; runtime validation of that combination remains outstanding.

patches-camera/0002 is automatically consumed by the existing apktool_patch
extraction hook. The local APK used as the build input was updated equivalently.
One existing class in classes.dex was replaced; every other DEX, native library,
resource, manifest and asset is byte-identical. Smali assembly and redisassembly
match exactly; applying the extraction patch produces the same class input.
The APK receives the platform signature through the existing android_app_import
build rule. No diagnostic transport helper is included in the production APK.

Local build input SHA-256:

- Before: `e3d83cc2d8c3bb51ff5d8308aa7a6ab0c3f5e24261f7a178ccf3d126b395d481`
- After: `4965a0e2ccbb80badf8cca6934ac95a0865b86e9aaae41e50feb872d0a179784`
