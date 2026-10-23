# Troubleshooting

## No PID, or more than one PID

Open the app and load its device list, then check the package name. Process IDs change when an app restarts. For a multi-process app, identify the device-data process explicitly; the guide refuses to select an arbitrary PID.

## Permission denied opening process memory

Check that `adb shell "su -c id"` reports `uid=0` and that the root manager granted access. Root alone may not override the phone's SELinux or process-access restrictions.

Do not disable system security globally just to make the scanner work. If the phone cannot provide the required access, that environment is unsupported.

## The app detects root or exits

Root detection can stop an app before it loads device data. Some historical sessions could capture already-loaded data before an app exited, but that behaviour is app- and version-dependent.

The scanner does not bypass root detection or app integrity checks. Do not assume that a patched APK or a proxy certificate will solve them.

## The binary will not run

Check the phone architecture with `adb shell getprop ro.product.cpu.abi`. The documented compiler produces ARM64 code; it will not run on an incompatible architecture.

Ensure the binary is executable and that you built the static version shown in the guide. A loader error can mean the wrong architecture or an unresolved runtime dependency.

## Capture is empty

Check the private scan log, the command's exit status, the current PID and whether the app actually loaded the relevant devices. The scanner skips unreadable regions and private mappings larger than 200 MiB.

An empty capture does not prove a key is absent. It may not be resident, may use a different representation, or may be outside the scanner's coverage.

## Capture contains matches but the parser returns `[]`

The parser accepts complete flat JSON objects. It cannot reconstruct nested or truncated records, or decode arbitrary app-specific structures.

Inspect the capture privately. If a record is simply longer than the default context, a new capture with `--context 4096` may help, but context is still clipped at chunk boundaries. Nested objects still need private inspection regardless of context size.

Do not upload a capture for debugging. Construct a synthetic example with invented data if you need to demonstrate a format issue.

## Multiple keys appear for one device

Memory can retain old or repeated records. Match the current device identity and validate the key with a read-only status check. The parser deduplicates identity/key pairs; it does not determine which key is current.

## The key does not work locally

Verify that the key belongs to that exact device and has not changed after pairing or reset. Check the device address, protocol version and whether it exposes a compatible local interface. A recovered key alone cannot establish those facts.
