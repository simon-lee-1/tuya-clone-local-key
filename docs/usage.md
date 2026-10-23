# Rooted Android guide

Use this procedure only with apps, accounts, phones and devices you own or are authorised to inspect. A logged-in app can hold account tokens and other private data alongside device keys.

The commands below run on a Linux computer connected to an **already-rooted ARM64 Android phone**. Rooting and bootloader unlocking are separate, device-specific tasks; unlocking commonly erases the phone. This guide does not flash firmware or unlock a bootloader.

## 1. Prepare the computer and phone

Install Python 3.9+, ADB and the ARM64 cross-compiler. On Debian/Ubuntu-based systems:

```bash
sudo apt-get install adb gcc-aarch64-linux-gnu python3 build-essential
```

Enable USB debugging on the phone and authorise your computer. Install and log in to the original vendor app normally. Its devices must already be paired and visible.

Check the connection, CPU architecture and root access:

```bash
adb devices
adb shell getprop ro.product.cpu.abi
adb shell "su -c id"
```

The build below expects `arm64-v8a`. The root check should report `uid=0`. If multiple Android devices are attached, select your phone with ADB's `-s` option on each command.

The vendor app may need Internet access to load its device records. The scanner and offline parser do not contact a cloud service.

## 2. Build the scanner

Run from the repository root:

```bash
umask 077
mkdir -p build
aarch64-linux-gnu-gcc -std=c11 -Wall -Wextra -Werror -O2 -static \
  -o build/tuya-memscan tools/memscan.c
```

This produces a statically linked ARM64 executable. Other architectures require a matching compiler and separate verification.

## 3. Select the app process

Open the vendor app and visit its device list or device details so it loads the records.

Find its package name locally:

```bash
adb shell pm list packages
```

Set `PACKAGE` to the package name of your own vendor app. The value below is a placeholder:

```bash
PACKAGE=com.vendor.ownedapp
PID=$(adb shell "pidof $PACKAGE" | tr -d '\r')
case "$PID" in
  *[!0-9]*|'') echo 'Expected one numeric app PID; check the running app'; exit 1 ;;
esac
```

If the app restarts, find its PID again. If it has multiple processes, identify the process that loads the device records; do not scan unrelated apps.

## 4. Deploy and capture

```bash
adb push build/tuya-memscan /data/local/tmp/tuya-memscan
adb shell "su -c 'chmod 755 /data/local/tmp/tuya-memscan'"

umask 077
mkdir -p captures
session_dir=$(mktemp -d captures/session.XXXXXX)

timeout 90 adb exec-out \
  "su -c '/data/local/tmp/tuya-memscan $PID localKey --context 500'" \
  > "$session_dir/matches.bin" \
  2> "$session_dir/scan.log"
capture_status=$?
printf 'Capture exit status: %s\n' "$capture_status"
```

Approve the root request on the phone if prompted. `mktemp` creates a private session directory; the restrictive umask creates capture files with mode 600. Keep using the same terminal so `$session_dir` and `$PID` remain set.

`adb exec-out` keeps the capture as a byte stream. Do not pipe it to the terminal, `tee`, a public paste service or an issue report.

An exit status other than zero means the command did not finish normally. A timeout can leave a partial capture. Even a zero status does not prove every mapping was readable: inspect the private scan log and the limitations below.

## 5. Parse supported records

Start with redacted output:

```bash
python3 tools/extract_local_keys.py \
  --input "$session_dir/matches.bin"
```

The parser reports fingerprints and deduplicates repeated records. To save full keys privately:

```bash
python3 tools/extract_local_keys.py \
  --input "$session_dir/matches.bin" \
  --include-keys \
  --output "$session_dir/local-keys.json"
```

The output path must not already exist or be a symlink. The parser creates it with mode 600 and refuses to print full keys to standard output.

**Parser scope:** it recognises complete, flat JSON objects containing a 16-character printable ASCII `localKey`. Nested objects, truncated records, escaped JSON strings and other encodings may not be recognised. Read [compatibility and limits](compatibility.md) before interpreting an empty result.

## 6. Associate keys with devices

The private export contains `record_fingerprint`, `key_fingerprint` and `local_key`. It deliberately does **not** export device names, IDs or IP addresses.

Inspect the capture in a local editor that can handle binary files, with cloud sync and sharing disabled. Where available, match `devId`, `deviceId` or `id` and the device name against your own app. Use the `localKey` from that same complete device record. Do not assign keys by list position or by whichever match appears first: memory can contain duplicate or stale records.

If the parser cannot handle a nested record, the captured JSON may still contain the key and its device identity. Inspect that record privately rather than treating an empty export as proof that no key exists.

Use your chosen local integration's read-only status check, if available, to validate the matching device ID and key. Extracting a key alone does not establish the LAN address, protocol version or supported device functions.

## 7. Clean up

Remove the executable from the phone:

```bash
adb shell "su -c 'rm -f /data/local/tmp/tuya-memscan'"
```

Keep any needed keys in private storage and remove captures when no longer needed. The repository ignores `captures/` and `build/`; those exclusions are not a substitute for checking what you commit.
