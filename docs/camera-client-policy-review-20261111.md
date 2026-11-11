# Camera client identity service policy

Stock vendor_sepolicy.cil grants cameraserver_30_0 find on
hal_cameraMDM_hwservice and Binder call/transfer to hal_cameraMDM_default.
The current combined policy omitted both permissions. Assign cameraserver to
the existing vendor_hal_cameraMDM client attribute; its existing HAL rules
provide the actual service/Binder permissions. No application receives them.

This is required by the companion extraPatches frameworks,av/0004 hook:
CameraServiceExtImpl::beforeConnect forwards the validated calling package
to cameraMDM before CamX configures OEM streams. Without that native hook,
the access rule alone does not deliver the package name.

The expanded full policy passes checkpolicy with neverallows enabled; an
effective policy inspection confirms find, Binder call/transfer and fd use.
The next full build must regenerate the images. Current-device video still
fails with -38; this source change has not been flashed or runtime-validated.
