# Credits and provenance

## Memory scanner

Credit for the published scanner belongs to **Simon Lee's Tuya extraction research**, distributed under the [MIT License](LICENSE), with copyright **2026 Simon Lee**.

The recorded source history introduces this `tools/memscan.c` implementation on **9 September 2026** in the maintainer's private research repository. It follows an earlier `memdump4.c` prototype preserved in the extraction notes. The later implementation adds bounded arguments, `pread`, chunk-boundary search overlap and an offline file-test mode.

This public repository imported that implementation on 24 October 2026. Its source header now retains the copyright and license identifier and points to this provenance record.

No third-party source URL or author attribution appears in the archived prototype or the original scanner addition. An earlier external origin is **not established** by the available records; this note does not assign credit to an unrelated project merely because it has a file called `memscan.c`. If an earlier source is identified, its attribution and license should be recorded here.

## README layout

The README's Features, Quick Start and Documentation layout was inspired by [vineetchoudhary/tuya-local-key](https://github.com/vineetchoudhary/tuya-local-key). That project's QR-login workflow is separate from the memory-scanning method documented here.

## Demonstration data

The [fixtures](fixtures/README.md) contain invented device records and demonstration keys. They are not excerpts from a real device capture.
