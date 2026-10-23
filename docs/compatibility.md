# Compatibility and limits

## Intended use

This project is for third-party, vendor-branded Tuya apps and Tuya clones whose devices cannot be added to the official Tuya Smart or Smart Life apps. A vendor app can use the Tuya/ThingClips SDK while keeping its account and device namespace separate.

The method requires:

- Your own logged-in vendor app with the relevant devices loaded.
- A rooted Android environment that lets the scanner read that app process.
- A plaintext representation of the device's local key in readable process memory.

It does not depend on enrolling the device in a Tuya IoT developer project.

## Confirmed result

**We successfully extracted local keys from two third-party Tuya apps.** We do not disclose which apps, their package names, account details, device inventories or captures.

This is a historical result for the extraction method. The included scanner and parser have offline synthetic tests; this publication is not a new live test against the latest versions of those apps. Compatibility with other apps, operating systems or future releases is not guaranteed.

## Why reading memory can work

An app may encrypt its network payloads and disk storage while keeping decrypted device records in memory for normal operation. The recorded successful extractions found JSON data containing `localKey` after the app had decrypted it.

The scanner observes data inside the authorised process after decryption. It does not decrypt stored MMKV files, reproduce cloud request signing or remove TLS certificate pinning. Root detection and integrity checks can still prevent an app from running or loading the records.

## Scanner limits

- Reads `/proc/<pid>/maps` and `/proc/<pid>/mem` for the selected process.
- Scans readable private mappings up to 200 MiB each; larger mappings are skipped.
- Reads in 64 KiB chunks, with overlap to detect a search term spanning a chunk boundary.
- Accepts search strings of 1–4096 bytes and context of 0–4096 bytes per side.
- Context can be truncated at chunk or mapping boundaries. Detecting a search term does not guarantee that the surrounding JSON object is complete.
- Unreadable regions may be skipped. A zero exit status is not a guarantee of complete memory coverage.

The documented ARM64 build is the supported starting point. Other architectures and Android security configurations need separate validation.

## Parser limits

The offline parser recognises complete **flat JSON objects**, up to 8192 bytes between their outer braces, containing `localKey` as 16 printable non-space ASCII characters.

Nested JSON, truncated objects, JSON embedded inside strings, UTF-16 data, keys stored separately from their record, or different field names may need private manual inspection or different tooling. Increasing the scanner's context does not change the parser's supported JSON shape.

The exported records contain key and record fingerprints, plus the key when explicitly requested. Device IDs, names, IPs and protocol versions are not included. Associate each key with its source device before using it.

## What a recovered key establishes

A key is one input to a compatible local integration. It does not guarantee that a device exposes a reachable LAN protocol or supports every function locally.

Device discovery and local control are separate: silence on UDP discovery ports does not prove there is no local interface. Conversely, possessing a key does not turn a cloud-only or gateway-dependent device into a directly controllable Wi-Fi device.

Re-pairing or resetting a device can change its local key. A record left in memory may be stale, so validate it against the matching device.
