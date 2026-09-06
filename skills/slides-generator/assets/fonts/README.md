# Exact Euclidean font assets

These five **unmodified static TrueType fonts** provide the exact families and
weights requested by the Euclidean slide design. They were downloaded from
Adobe's official `adobe-fonts` GitHub repositories on 2026-09-06. They are local
application assets, not installed system fonts. No font substitution, renaming,
subsetting, format conversion, or synthetic weight was applied.

[`fonts.json`](fonts.json) provides the renderer's machine-readable manifest.
Its `file` and `license_file` paths are relative to this directory. Manifest
styles match the extracted design exactly: `Regular`, `Bold`, `SemiBold`, and
`Black`; `SemiBold` maps to Adobe's unchanged `SourceSansPro-Semibold.ttf`.
Bundling these files enables local font measurements but does not install them
in the OS or embed them in a PowerPoint document. A recipient must install the
exact fonts for PowerPoint to reproduce their appearance without substitution.

The current repository names are `source-serif` and `source-sans`, but these
historical releases contain **Source Serif Pro** and **Source Sans Pro**.
Do not replace them with Source Serif 4 or Source Sans 3: those are different
internal family names and may have different metrics.

## Official releases and immutable revisions

| Family | Official release/tag | Git commit |
| --- | --- | --- |
| Source Serif Pro | [3.001R](https://github.com/adobe-fonts/source-serif/releases/tag/3.001R) | `c811345609ee81ddb83ac707c15f7defd6269963` |
| Source Sans Pro | [2.045R-ro/1.095R-it](https://github.com/adobe-fonts/source-sans/releases/tag/2.045R-ro/1.095R-it) | `ce77773581f4d454f0fa985c073bb25c721bfcf5` |

### Per-file download provenance

Each URL below is the original download URL. Serif uses the release tag; its
immutable equivalent replaces the tag with the corresponding commit above.
Sans URLs already use the immutable commit of the listed release tag (whose
roman fonts are version 2.045; no italic fonts are bundled).
The license files are the original release `LICENSE.md` (Serif) and
`LICENSE.txt` (Sans) bytes, renamed locally only to distinguish the two notices.

| Local file | Release/tag | Original source URL |
| --- | --- | --- |
| `SourceSerifPro-Regular.ttf` | `3.001R` | <https://raw.githubusercontent.com/adobe-fonts/source-serif/3.001R/TTF/SourceSerifPro-Regular.ttf> |
| `SourceSerifPro-Bold.ttf` | `3.001R` | <https://raw.githubusercontent.com/adobe-fonts/source-serif/3.001R/TTF/SourceSerifPro-Bold.ttf> |
| `LICENSE-SourceSerifPro.md` | `3.001R` | <https://raw.githubusercontent.com/adobe-fonts/source-serif/3.001R/LICENSE.md> |
| `SourceSansPro-Regular.ttf` | `2.045R-ro/1.095R-it` | <https://raw.githubusercontent.com/adobe-fonts/source-sans/ce77773581f4d454f0fa985c073bb25c721bfcf5/TTF/SourceSansPro-Regular.ttf> |
| `SourceSansPro-Semibold.ttf` | `2.045R-ro/1.095R-it` | <https://raw.githubusercontent.com/adobe-fonts/source-sans/ce77773581f4d454f0fa985c073bb25c721bfcf5/TTF/SourceSansPro-Semibold.ttf> |
| `SourceSansPro-Black.ttf` | `2.045R-ro/1.095R-it` | <https://raw.githubusercontent.com/adobe-fonts/source-sans/ce77773581f4d454f0fa985c073bb25c721bfcf5/TTF/SourceSansPro-Black.ttf> |
| `LICENSE-SourceSansPro.md` | `2.045R-ro/1.095R-it` | <https://raw.githubusercontent.com/adobe-fonts/source-sans/ce77773581f4d454f0fa985c073bb25c721bfcf5/LICENSE.txt> |

### SHA-256 and uncompressed file sizes

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `SourceSerifPro-Regular.ttf` | 231036 | `bbe1e33dfabbfe69b97564724bf763918ea582ad03d8cc066e42dc74eb1e17c7` |
| `SourceSerifPro-Bold.ttf` | 233952 | `68d8a1f66a665c1fd17f06a76cab986d9cd3c4ed4f42c41b1b3121acdb8325b4` |
| `SourceSansPro-Regular.ttf` | 254076 | `c6f835b6a6d942b196e2607bf73a7b086407ae8dbdc928c23a2fb4893ec383f6` |
| `SourceSansPro-Semibold.ttf` | 253832 | `72bf9aa2e78b8c78444ae74b6be09411d5fb5bf0eb9bcdfd47082cc5d9b536df` |
| `SourceSansPro-Black.ttf` | 253584 | `4183f9ae34bd50bde1ee5601302c0d1666638cad52ff2a8886d8c47535be1999` |
| `LICENSE-SourceSerifPro.md` | 4578 | `80c6ab285b3ee07cfd7ee0c4d682a79d250240925ebe6af74bb929736cab0b87` |
| `LICENSE-SourceSansPro.md` | 4579 | `e1d1fdcefb57985226c06fa9500d29caacfa2b1f8b8c74db911f13c6cad186a1` |

The five font binaries total **1,226,480 bytes (about 1.17 MiB)**. The two
original license files add 9,157 bytes, excluding this README.

## Copyright and license

Both families are licensed under the **SIL Open Font License, version 1.1
(26 February 2007)**, not the template's Creative Commons license. The complete,
authoritative notices and license terms accompany the fonts:

- [Source Serif Pro license](LICENSE-SourceSerifPro.md): “Copyright 2014-2019
  Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. All Rights
  Reserved. Source is a trademark of Adobe in the United States and/or other
  countries.”
- [Source Sans Pro license](LICENSE-SourceSansPro.md): “Copyright 2010-2018
  Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. All Rights
  Reserved. Source is a trademark of Adobe in the United States and/or other
  countries.”

The embedded font copyright records additionally say “© 2014 - 2019 Adobe
Systems Incorporated” for Serif and “© 2010 - 2018 Adobe Systems Incorporated”
for Sans, with Reserved Font Name ‘Source’. Both are preserved exactly
as published. Embedded designer credits are
Frank Grießhammer (Serif) and Paul D. Hunt (Sans).

Summary only; the full included licenses control:

- Use, study, copy, embed, modify, and redistribute are permitted, including
  bundling with commercial software. Fonts must not be sold by themselves.
- Redistributed copies must retain the copyright notice and OFL license.
- Modified fonts cannot use the Reserved Font Name without written permission.
  These bundled originals have not been modified.
- Copyright-holder and author names cannot endorse modified versions without
  permission, except to acknowledge their contribution.
- The font software remains under OFL 1.1; documents created with it do **not**
  have to use OFL. There is no warranty. Breaching the conditions terminates
  the license.

## Verified identity and renderer metrics

Verification read the binaries directly using Python's standard-library
`struct` parser: the sfnt table directory and checksums, `name`, Unicode `cmap`
formats 4/12, `head`, `hhea`, `OS/2`, and `maxp`. No dependency or global font
installation was needed. All table and whole-font checksums passed. All seven
downloaded files were also compared byte-for-byte against the official raw
URLs at the immutable commits above; every comparison and manifest hash passed.

| File | Effective family | Style | `usWeightClass` | PostScript name |
| --- | --- | --- | ---: | --- |
| `SourceSerifPro-Regular.ttf` | Source Serif Pro | Regular | 400 | SourceSerifPro-Regular |
| `SourceSerifPro-Bold.ttf` | Source Serif Pro | Bold | 700 | SourceSerifPro-Bold |
| `SourceSansPro-Regular.ttf` | Source Sans Pro | Regular | 400 | SourceSansPro-Regular |
| `SourceSansPro-Semibold.ttf` | Source Sans Pro | Semibold | 600 | SourceSansPro-Semibold |
| `SourceSansPro-Black.ttf` | Source Sans Pro | Black | 900 | SourceSansPro-Black |

“SemiBold” in the design request corresponds to Adobe's internal spelling
“Semibold”, weight 600. For Sans Semibold and Black, the typographic family
(`name` ID 16) is `Source Sans Pro`, and ID 17 specifies the weight. Their legacy
ID 1 family names are respectively `Source Sans Pro Semibold` and
`Source Sans Pro Black`, with legacy subfamily `Regular`. Other files use
family ID 1 and subfamily ID 2 without needing IDs 16/17. A renderer should load
the exact file for the requested weight, not synthesize bold from Regular.

All five files have **1000 units per em** and `OS/2.fsType = 0` (no technical
embedding restriction; the OFL terms still apply). Serif is version 3.001,
Sans is version 2.045. These are static outlines, not variable fonts.

| Family/style | Ascender | Descender | Line gap | Cap height | x-height | Glyph count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Serif Regular / Bold | 1036 | -335 | 0 | 670 | 475 | 1450 |
| Sans Regular | 984 | -273 | 0 | 660 | 486 | 1974 |
| Sans Semibold | 984 | -273 | 0 | 660 | 491 | 1974 |
| Sans Black | 984 | -273 | 0 | 660 | 500 | 1974 |

Ascender/descender/line-gap above are `hhea` values. Serif agrees with OS/2
typographic metrics; Sans OS/2 typographic metrics are instead 750/-250/0.
OS/2 Windows ascent/descent are 1036/335 for Serif and 984/273 for Sans.
These are font units: multiply by font size / 1000 to obtain scaled
metrics. The `hhea` metric line spans are therefore 1.371 em and 1.257 em,
respectively; they are **not** instructions to override the template's explicit
line-height or baseline placement.

Every file maps all **66 Russian upper/lowercase letters, including Ё and ё**,
to nonzero glyph IDs. Each maps 150 code points in U+0400–U+04FF, not the whole
Cyrillic block. Every character in this sample has a glyph in all five files:

> Съешь ещё этих мягких французских булок, да выпей чаю. Презентация: Ёжик — 2026 № 1.

This is binary character-coverage validation, not a claim that a specific
application's shaping, font registration, or final rendered layout was tested.

### Choosing the closer Source Sans Pro release

The initial 3.006 candidate was replaced by original Adobe version 2.045 after
comparing glyph advances against the supplied scene, without publishing scene
identifiers or text. On ASCII-only text nodes, applying their declared uppercase
or lowercase transform and measuring individual characters with Pillow at
1000 px, the following aggregate differences were observed (units: em):

| Style | Compared glyph records | 3.006 maximum / mean error | 2.045 maximum / mean error |
| --- | ---: | --- | --- |
| Regular | 1992 | 0.001 / 0.00025905 | 0.0000000577 / 0.0000000220 |
| SemiBold | 375 | 0.003 / 0.00101865 | 0.0000000644 / 0.0000000235 |
| Black | 23 | 0.0000000644 / 0.0000000244 | 0.0000000644 / 0.0000000244 |

Version 2.045 thus matches these recorded advances to floating-point precision
and its `hhea` line span 1.257 em agrees with the scene's Sans natural line
height (3.006's span was 1.424 em). All three weights retain the complete Russian
alphabet. The Serif files were left unchanged.

This establishes a closer **metrics match**, not the identity of the original
font binary or its exact release version. The candidate files' base64 SHA-1
values did not equal the scene's recorded font-digest values; the scene's digest
algorithm is not established here. No binary-identity claim is made.

## Separate Figma template licensing research

The font permissions above are independent of permissions for the slide
template. On 2026-09-06 the public official
[Figma Community copyright and licensing policy](https://help.figma.com/hc/en-us/articles/360042296374-Figma-Community-copyright-and-licensing)
was successfully retrieved. Its **“Slide deck templates”** section explicitly
says that templates are published under CC BY 4.0, are not public domain, may
have additional license types, and may be shared/adapted for any purpose
including commercial purposes, with creator credit.

The [CC BY 4.0 deed](https://creativecommons.org/licenses/by/4.0/) was also
retrieved. It requires appropriate credit, a license link, and indication of
changes, without implying endorsement or imposing additional restrictions.
See the [actual legal code](https://creativecommons.org/licenses/by/4.0/legalcode)
for governing terms.

The specific [Euclidean Community page](https://www.figma.com/community/file/1387141600584938870/euclidean)
returned **HTTP 403** on direct retrieval. Search results indexed that exact
official URL and reported “nicholas@jitkoff.com CC BY 4.0”, but that is
search-index evidence, **not independently verified page content**. The name
**Nicholas Jitkoff** is the supplied attribution. We did not verify the page's
current creator metadata, any additional terms, or rights for every embedded
third-party asset. No private account or user data was used.

Suggested template credit, based on the supplied attribution and verified
general slide-template policy (not a claim to have accessed the blocked page):

> Adapted from “Euclidean” by Nicholas Jitkoff,
> https://www.figma.com/community/file/1387141600584938870/euclidean.
> Licensed under CC BY 4.0, https://creativecommons.org/licenses/by/4.0/.
> Changes: adapted slide content and implementation.

Keep the template credit and applicable adaptation notices with template-derived
outputs or their accompanying credits; keep these OFL notices with redistributed
font files.
