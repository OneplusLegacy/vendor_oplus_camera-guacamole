# Camera property context review (2026-11-11)

The reference `vendor/oplus/camera/sepolicy/vendor/property_contexts` labels
`ro.oplus.system.camera.name` and the `vendor.camera.*` prefix as
`vendor_camera_prop`. The guacamole port declared the values in
`PRODUCT_VENDOR_PROPERTIES` but omitted these labels.

The current assembled contexts resolve the package name to `default_prop`.
`init/property_service.cpp::LoadProperties` loads vendor/odm build properties
using `vendor_init`; the compiled policy grants this domain no setter for
`default_prop`. Consequently the name cannot be initialized from vendor props.
The JPEG flag resolves to `vendor_default_prop`, which vendor_init can set and
the camera HAL can read, but opluscamera_app and shell cannot read. Empty app
and shell queries do **not** establish that this second property is unset.
Both names returned empty from instrumentation running inside the camera app.
Reading the raw device /vendor/build.prop was permission denied.

Add exact labels for these two settings, preserving unrelated property labels.
The existing policy already allows vendor_init to set vendor_camera_prop and
opluscamera_app / hal_camera_default to read it; no new allow rule is needed.
The shipped API level is 28, so this legacy stock ro.oplus property is permitted
by the vendor property namespace build check (which is enforced from API 29).

Verification: property_info_checker with all five built property contexts plus
the proposed exact entries; checkfc -p against the current compiled policy;
resolution of all six port-declared vendor properties. Run the coverage check
without --extra-contexts after rebuilding to inspect the newly assembled map.
Product Lens properties already appear in device getprop and are outside this
vendor-init label check.

This repairs a real omission in reference integration. It does not demonstrate
that video recording is repaired. The latest diagnostic APK still gets HAL
configureStreams -38 for session 0x8116 and sensor-mode index -1. Full image
build/flash and runtime video verification remain necessary.
