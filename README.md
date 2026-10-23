[![Offline tests](https://github.com/simon-lee-1/tuya-clone-local-key/actions/workflows/offline-tests.yml/badge.svg)](https://github.com/simon-lee-1/tuya-clone-local-key/actions/workflows/offline-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# Tuya Clone Local Key

Recover device local keys from **third-party Tuya-based Android apps and Tuya clones**, including devices that cannot be added to the official **Tuya Smart or Smart Life** apps.

This method uses a **rooted Android phone** running the original vendor app, logged in to your own account. It searches the app's memory for device records after the app has decrypted them. No Tuya IoT developer account, cloud project or API subscription is required.

**We have successfully extracted local keys from two third-party Tuya apps using this method.** The app names and identifying details are intentionally omitted. Compatibility with other apps or future versions is **not guaranteed**.

## Features

- Recover keys for devices confined to a vendor-branded Tuya app.
- Read device data after decryption, even when the app's disk storage and network payloads are encrypted.
- Search one selected app process for `localKey`, with bounded context around each match.
- Parse supported records offline, with key fingerprints shown by default.
- Export full keys only to a new private file with mode 600.
- Run the included tests entirely offline using synthetic data.

The repository publishes the extraction method and existing command-line tools. The two-app result refers to the method used in the original extraction sessions; automated tests validate the included tools with synthetic fixtures.

## Quick Start

### Try it offline

Requires Python 3.9 or newer. This uses fake records and does not connect to a phone or account.

```bash
git clone https://github.com/simon-lee-1/tuya-clone-local-key.git
cd tuya-clone-local-key
python3 tools/extract_local_keys.py --input fixtures/synthetic_memory.fixture
```

The output contains record and key fingerprints, with no full keys or raw device identifiers. The [synthetic fixtures](fixtures/README.md) use explicitly invented `FAKE` values, never captured device keys.

### Extract from your vendor app

You need an already-rooted Android phone, ADB, your logged-in vendor app, and devices already visible in that app.

1. Build the scanner for your phone's architecture.
2. Open the vendor app's device list and identify its process.
3. Capture matches for `localKey` into a private local file.
4. Parse supported records and associate each key with its device privately.
5. Remove the scanner from the phone when finished.

Follow the [rooted Android guide](docs/usage.md) for commands, prerequisites and cleanup. The documented build targets ARM64 Android from a Linux computer.

The helper parser accepts **flat JSON objects**. Apps that keep records in nested JSON or another representation may require private inspection of the capture; an empty parser result does not prove that extraction failed. See [compatibility and limits](docs/compatibility.md).

### Run the tests

Requires Python 3.9+ and a C compiler available as `cc`.

```bash
python3 tests/test_memscan.py
python3 tests/test_extract_local_keys.py
```

Tests do not use ADB, root, accounts, cloud APIs or real devices.

## Documentation

- [Rooted Android guide](docs/usage.md) — build, capture, parse, identify and clean up.
- [Compatibility and limits](docs/compatibility.md) — supported scenarios, two-app result and parser constraints.
- [Troubleshooting](docs/troubleshooting.md) — root access, missing matches and incomplete records.
- [Handling captures and keys](docs/security.md) — private files and safe issue reports.
- [Credits and provenance](CREDITS.md) — scanner origin, copyright and source-history limits.

## Related Project

[vineetchoudhary/tuya-local-key](https://github.com/vineetchoudhary/tuya-local-key) provides a QR-login workflow for Smart Life / Tuya devices and inspired this README's layout. This independent project covers vendor-app scenarios where devices cannot be brought into those official apps. It does not use that project's QR-login implementation.

## License

Licensed under the [MIT License](LICENSE).
