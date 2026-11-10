# 7 Pro framework, APK patch and permission review

The reference hardware/oplus HEAD contains reverts. Compare its pre-revert
852ccb0 clients; do not restore its full OOS16 feature/binder surface onto 7 Pro.

Instruction-level DEX analysis found the camera thumbnail using the bundled
stub OPlusAccessControlManager. The adapter reports the OEM lock backend absent;
it never fabricates a passed authentication result. Android lock enforcement is
still performed by the actual system. Gallery's font helper directly loads the
OplusBaseConfiguration type on Android12+. Add the reference's type token but
keep AOSP Configuration unrelated to it, so the existing isInstance check selects
the default font. Its extra theme fields are longs in this APK, unlike the older
reference's int mThemeChangedFlags. Add the exact hasFeatureIPC descriptor too.

The many remaining compatibility-library references are not all live failures:
Gallery's Context/BitmapFactory/StorageVolume wrappers have an Android SDK31+
branch that precedes older com.oplus.inner calls. HEIF proprietary paths are
feature-gated and remain outside this patch; no different-device decoder is
substituted. The scan does not prove every reflection/JNI path is functional.

## APK patch handling

camera-guacamole previously had no blob_fixups. It now explicitly applies
patches-camera to OnePlusCamera.apk during extraction. The new patch requests
SYSTEM_CAMERA, already present in the privileged allowlist but absent from the
original manifest. Current CameraService checks it for system-only cameras;
this corrects capability access, not proof that every lens/capture mode works.
The current local prebuilt is rebuilt with the same patch. The original DEX,
all native libraries and service metadata are preserved, and all 7155 resource
ids/names remain unchanged. The original APK is retained outside the source tree.

Reference patch selection:
- Default font: solve this APK's missing configuration ABI with the matching
  reference type token. Do not apply the unrelated obfuscated ia/y3 method.
- OEM permissions: retain guards; define only the four consumed permissions in
  a platform-signed system_ext permission package. Do not remove every guard.
- Task observation: no task-listener/floating-window feature is advertised here;
  do not request its extra privileged permissions speculatively.
- Unit SDK fixes and face-beauty fallback: the 7 Pro does not ship the reference
  com.oplus.camera.unit.sdk.jar; its APK embeds different code and native libs.
- Gallery ActionReceiver export flags: 7 Pro Gallery targets31, Camera targets29;
  the Android14+ explicit-export compatibility requirement is not enabled by
  default for these targets. Preserve explicit export intent if later retargeted.
- Gallery theme/live-photo patches: different resources/modes; not copied or
  force-enabled without matching implementation and capability evidence.

## SELinux and permission evidence

Compare effective allows from stock ODM precompiled_sepolicy and the compiled
candidate policy using this ROM's libsepol (host setools cannot parse Android17
policy extensions). Expand source/target attributes before comparing. Relevant
remaining shared-type differences included camera_update, the QTI camera property
type, the optional DSP-manager service and DMS-to-audioserver binder callbacks.
Restore camera_update directory/file access and read-only vendor_persist_camera_prop
access. Both target types and their consumers exist in this tree. No raw device
or global vendor-file access is added. The DSP-manager daemon is absent from the
current image; no service/permission is invented for it. DMS currently receives
its effect client from hal_audio_default, already allowed; a direct audioserver
client was not added merely because stock has a different hosting path.

Stock camera/gallery privileged permission entries are covered by the existing
allowlist. SYSTEM_CAMERA additionally needs the APK request above. Camera helper
FORCE_STOP_PACKAGES and Gallery WRITE_MEDIA_STORAGE/WRITE_SECURE_SETTINGS/
SCHEDULE_EXACT_ALARM are granted in the live package state. Runtime photo/video
permissions and AppOps are separate: Gallery was ungranted/ignored in the audit,
Camera's capture/audio/media grants were present. User privacy choices are not
forced through a default grant or shell pm grant.

GuacamoleOplusPermissions defines only these signature permissions consumed by
existing APK component guards: oplus.permission.OPLUS_COMPONENT_SAFE,
com.oplus.permission.safe.SECURITY, com.oppo.permission.safe.SECURITY and
com.oplus.permission.safe.LOG. Both production apps are platform signed, so they
can receive them; unrelated signers cannot. It does not implement absent Heytap
cloud, sticker-provider or document-vault services.

Validation: compiled actual framework clients and checked field descriptors,
lock results and feature query; APK rebuilt/resource IDs/native entries checked;
permission package resources linked; candidate neverallow policy compiled.
Next ROM runtime validation remains required for permission grants, media access,
font/theme handling, camera modes and callback/DSP paths.

## Follow-up after the user's runtime permission choice

The user granted Gallery photo/video permissions; package state confirms them.
This then exposed an unconditional OplusActivityManager construction in
AppUiResponder/ZoomWindowManager. Add a constructor without IPC and typed AOSP
task queries with the system's existing caller filtering, no OEM transaction
numbers and no invented parental-control implementation. Restore the referenced
OplusAppInfo Parcelable and avoid sharing mutable bounds in its copy constructor.
The Gallery GLView also constructs LongshotCustomController. Match the actual
7 Pro OplusLongshotViewInfo (single int boolean) and correct the reference's
Longshow/Longshot type-name mistake. Report OEM longshot unsupported rather than
claiming an absent service works. Preserve the SDK default feature object when
its vendor index is absent; retain null-input rejection and parameter checking.

An updated diagnostic Gallery APK includes these selected compatibility classes.
No production camera APK, permission-definition APK, policy, boot jar or ROM was
installed on the phone during this follow-up. Source changes require a new ROM.

## Final follow-up (2026-11-11)

The Gallery scan worker unconditionally constructs OplusWhiteListManager after
media access is granted. Supply that client without creating a nonexistent OEM
stage-protection backend. Match all actual APK return descriptors: notably,
getGlobalProcessWhiteList returns ArrayList, whereas the older hardware/oplus
reference declares List. The query lists are independent empty hint lists;
add/remove hints do not alter Android's process or application security policy.
The actual client and ABI/mutation-isolation checks are committed in
hardware/oplus-guacamole (2c0ccb8).

An 18-client, same-certificate Gallery diagnostic update was installed without
clearing user data. The selected Java sources match the committed framework
sources. The user confirmed that editing works after this update; no new Gallery
crash appeared in the subsequent crash-buffer read, and user-selected image,
video and media-location permissions remained granted. This is evidence for the
reported editing failure, not exhaustive testing of every editor feature. The
permanent boot-framework clients require the next ROM; the diagnostic APK is a
/data update and should be accounted for when testing that ROM's stock APK.

All 169 current framework Java sources, plus the generated zoom-observer AIDL,
compiled against the current Android framework with a bounded Java heap. This
checks source/descriptor consistency without a full ROM build. A DEX call-site
scan still flags compatibility-library branches for absent OEM APIs; its count
is not a count of reproducible failures. Android SDK dispatch and capability
checks must be examined before importing another implementation.

The native CameraService extension also had an unsynchronized load/singleton
path, a member call without its factory this argument and error statuses falling
through into the platform parser. extraPatches now supplies the 0003 camera
patch (c071ab2); the corresponding frameworks/av commit is 5060b6f3f5. It
serializes initialization, resolves the exported method with the correct object,
keeps ordinary Camera2 traffic out of the OEM parser and preserves handled
errors. Both modified ARM64 translation units passed syntax checks using the
current CFI build flags; six fake-loader/concurrency scenarios and replay of the
three camera patches passed. Stock binary dispatch is exactly 10001..10011, so
the first camera patch's original claim about transaction 10015 is not proof of
zoom support. See extraPatches/docs/camera-extension-review-20261111.md.

Remaining native observations:
- SNPE's remote_* imports request ADSPRPC/SDSPRPC versions while the current
  FastRPC providers export those symbols globally. Bionic's check_symbol_version
  explicitly accepts global definitions when the requested version is not
  defined by that DSO; the strict host check alone overstates these failures.
  No symbol version or vendor RPC library was patched on that basis.
- Optional SNPE *_system variants request libcdsprpc_system.so, while this device
  publishes libcdsprpc.so. The observed runtime selected the normal CDSP path;
  its logged firmware/SELinux errors are addressed by the existing RFSA images
  and narrow adsprpcd_file policy, requiring next-ROM verification.
- Gallery's libst_sticker_jni.so requests libst_mobile.so, which is absent from
  this extracted stock set. The 13T file name alone does not establish matching
  ABI. Advanced stickers are unverified; no unrelated binary is substituted.
- Proprietary OplusHeifConverter calls are capability-gated. Stock JNI depends
  on additional OEM decoder libraries and private graphics APIs; do not force
  this feature on or claim it works from AOSP HEIF support alone.

Camera lens switching, video, portrait, front/rear capture, new signature guard
permissions and the private camera ABI still need the next ROM runtime test.
The current flashed boot jar, policy and cameraserver do not contain these
source changes. Updating Gallery cannot validate those system components.
