#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#
# Stock OnePlus 7 Pro camera and gallery.
#
# Inherit from device/oneplus/guacamole/device.mk:
#   $(call inherit-product-if-exists, vendor/oplus/camera-guacamole/opluscamera.mk)
#
# Everything here comes from GM1911_11.H.41 (ColorOS 12.1 / Android 12). The
# placeholders that differ from the 13T port are called out inline.
#

PRODUCT_SOONG_NAMESPACES += \
    vendor/oplus/camera-guacamole

# ---------------------------------------------------------------------------
# Soong config
#
# libgui: OPCamera2CoreImpl allocates its redirect preview reader with 96
# image slots (RedirectHardwareBufferImageReader(..., 96, ...)). AOSP caps
# BufferQueue at 64, so the limit has to be raised and the product has to ask
# for it. Requires frameworks/native/0001-libgui-Allow-Num-Buffer-slots-to-be-
# increased.patch from vendor/extraPatches.
# ---------------------------------------------------------------------------
$(call soong_config_set,libgui,num_buffer_slots,96)

# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------
PRODUCT_PACKAGES += \
    OnePlusCamera \
    OnePlusCameraService \
    OnePlusGallery \
    GuacamoleOplusPermissions

# The CameraService extension (libcsextimpl) that cameraserver loads through
# the frameworks/av patch, plus the HIDL interfaces it links against.
#
# The camera and gallery bundle every library they dlopen (libOnePlusCamera,
# libCameraNext, the APS JNIs, the ARCSoft and Morpho pieces), and the only
# external names they reach for are platform or vendor libraries that this tree
# already ships. Nothing else from /my_product/lib64 is needed.
#
# Module names carry a guacamole_ prefix where they collide with the 13T port
# in vendor/oplus/camera; see the MODULE NAMING block in Android.bp.
PRODUCT_PACKAGES += \
    guacamole_libcsextimpl \
    guacamole_vendor.oplus.hardware.cameraMDM@1.0 \
    guacamole_vendor.oplus.hardware.cameraMDM@2.0 \
    guacamole_vendor.oplus.hardware.commondcs@1.0 \
    guacamole_vendor.oplus.hardware.performance@1.0

# ---------------------------------------------------------------------------
# Permissions
#
# Platform-signed privileged apps still need an allowlist entry for
# signature|privileged permissions, otherwise system_server aborts.
# ---------------------------------------------------------------------------
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/permissions/privapp-permissions-oneplus-camera.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/permissions/privapp-permissions-oneplus-camera.xml

# The camera and gallery reflect into framework internals. They are platform
# signed, which exempts them from the hidden-API blocklist by default, but the
# allowlist makes that explicit and survives a build that flips the default.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/sysconfig/hiddenapi-package-oneplus-whitelist.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/sysconfig/hiddenapi-package-oneplus-whitelist.xml

# ---------------------------------------------------------------------------
# Properties
#
# Values taken verbatim from the stock build:
#   /odm/build.prop and /vendor/build.prop  (camera name, aux package list)
#   /vendor/etc/permissions/android.hardware.camera.*.xml  (privapp list)
#
# ro.oplus.system.camera.name selects which package the framework treats as
# the privileged system camera. Stock 7 Pro sets it to com.oneplus.camera;
# the rest of the tree may still carry com.oplus.camera for the 13T, so this
# has to win.
# ---------------------------------------------------------------------------
PRODUCT_VENDOR_PROPERTIES += \
    ro.oplus.system.camera.name=com.oneplus.camera \
    ro.camera.notify_nfc=1 \
    vendor.camera.algo.jpeghwencode=0 \
    vendor.camera.aux.packagelist=android,com.oneplus.camera,com.oppo.camera,com.oppo.engineermode,com.oplus.camera \
    persist.vendor.camera.privapp.list=com.oneplus.camera,com.oppo.camera,com.oppo.engineermode,com.oplus.camera \
    persist.camera.privapp.list=com.oneplus.camera,com.oppo.camera,com.oppo.engineermode,com.oplus.camera

PRODUCT_PRODUCT_PROPERTIES += \
    ro.com.google.lens.oem_camera_package=com.oneplus.camera \
    ro.com.google.lens.oem_image_package=com.oneplus.gallery

# ---------------------------------------------------------------------------
# SELinux
#
# The stock 7 Pro gives com.oneplus.camera the default priv_app domain: there is
# no com.oneplus.camera entry in its seapp_contexts. The camera still has to
# execute vendor libraries (libadsprpc, libcdsprpc) and reach a few vendor
# data directories, so this port defines an opluscamera_app domain the same way
# the 13T port does and maps both packages onto it.
# ---------------------------------------------------------------------------
include vendor/oplus/camera-guacamole/sepolicy/SEPolicy.mk

# Hexagon firmware bundled in the stock camera APK, exposed to FastRPC.
PRODUCT_PACKAGES += \
    guacamole_camera_snpe_dsp_domains_skel \
    guacamole_camera_snpe_dsp_skel \
    guacamole_camera_snpe_dsp_v65_domains_v2_skel \
    guacamole_camera_snpe_dsp_v66_domains_v2_skel
