# Handling captures and keys

Process-memory captures can contain local keys, account tokens, device identifiers and other private data. A narrow search reduces the amount captured but does not make the output safe to share.

## Private output

- Set `umask 077` before creating captures.
- Use a private directory, such as the mode-700 session directory created by the guide.
- Keep capture files and key exports at mode 600.
- Keep files out of cloud-synced folders, terminal recordings, screenshots, commits and issue attachments.
- Remove the scanner from the phone when finished.

The parser's default output contains fingerprints. Full key export requires `--include-keys` and a new `--output` path; it refuses standard output, existing files and symlink targets.

The scanner's raw output is **not redacted**. Always redirect it to a private file, including its diagnostic log.

## Publishing or requesting help

Share the command shape, exit status, Android architecture and a synthetic reproduction where possible. Remove app and device identifiers if you want to keep them private.

Never post raw captures, key exports, account tokens, real device JSON, APK signing secrets or phone backups. Replacing only the `localKey` value does not remove other sensitive fields.

The committed fixtures are entirely synthetic. Neither the tested apps' identities nor any real extraction data is included.

## Local-only verification

The test suites compile and run the scanner against temporary files and exercise the parser with fake records. They do not connect to phones, accounts, devices or cloud services.

Live memory access is a separate, opt-in operation performed by the owner. This repository does not perform device actuation.
