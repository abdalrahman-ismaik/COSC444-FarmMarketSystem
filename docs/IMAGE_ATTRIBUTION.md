# Image attribution and provenance audit

**ATTR-01 | 17 November 2026 | Mohammad Arwani with Codex | Ready for review with an unresolved mapping dependency.**

The imported package attributes its images to Fruits-360 under CC BY-SA 4.0. This pass verified upstream dataset-level attribution and audited the local bytes. It did **not** establish a source-file match or dataset version for any of the sixteen local images. No photo was replaced. The report and poster add no produce-photo reproductions.

## Verified upstream sources

- [Current original-size README](https://github.com/fruits-360/fruits-360-original-size/blob/main/README.md), fetched 17 November 2026, identifies version **2026.10.26.0**, credits **Mihai Oltean, Fruits-360 dataset, 2017-**, and names CC BY-SA 4.0. README blob SHA: `a12b937f70d8e80995e98ce1577e90d4343c7eda`. This current version is **not** asserted to be the version used in our package.
- [Current original-size license](https://github.com/fruits-360/fruits-360-original-size/blob/main/LICENSE), blob SHA `c09f53ff8d604252e1c7fb2cd13241871e02e0a5`, carries the Mihai Oltean copyright notice and CC BY-SA 4.0.
- [Earlier repository README](https://github.com/Horea94/Fruit-Images-Dataset/blob/master/readme.md) identifies version 2020.05.18.0, points to the new organization, and cites Horea Muresan and Mihai Oltean's 2018 paper. Its 100x100 filename convention differs from our descriptive filenames and variable image dimensions. That is not proof that our images originate from that release or from the current original-size branch.
- [Creative Commons BY-SA 4.0 deed](https://creativecommons.org/licenses/by-sa/4.0/) summarizes attribution, license-link, change-indication and share-alike conditions. [Legal code](https://creativecommons.org/licenses/by-sa/4.0/legalcode) is the controlling license text. Dataset-level credit alone does not resolve the missing local source mapping.

Preserve the imported credit: **Fruits-360 dataset, CC BY-SA 4.0**. Current upstream recommended citation is **Mihai Oltean, Fruits-360 dataset, 2017-**. Record the matching release's actual credit once the source is identified; do not silently assign the current release's author/version to unmatched files.

## Local checks actually performed

Read `app/schema.sql`, four external JPEGs, archived README and the historical visual guide. Parsed the twelve SQL hex BLOB literals without executing SQL; inspected dimensions and EXIF through Pillow; computed SHA-256s. All sixteen images have no EXIF keys. Local filenames are generic crop labels and do not identify an upstream split/class/frame.

Compared each external JPEG and all twelve `(lot, filename, bytes)` BLOB tuples with `archive/original-package/FarmMarketSystem_Team.zip`: **4/4 external files and 12/12 BLOBs match exactly**. This proves preservation since import, not upstream authorship. The archive/guide contained only the dataset/license attribution, not original URLs or transformation records. No full-dataset image-matching search was performed; the dataset is large and local images may have been transformed.

Reproduce the local inventory with `python docs/report/build_documents.py`; inspect ignored `output/documents/image-inventory.json`. Document dependencies are in `docs/report/requirements-docs.txt`. This check uses no database or credentials.

## Asset register

For every row below, **exact original URL, creator of that specific image, dataset version, and prior resizing/cropping/re-encoding history remain unknown**. Dimensions are width x height. External paths are beneath `app/`; SQL entries are in `app/schema.sql`.

| Local asset | Bytes | Pixels | SHA-256 |
|---|---:|---|---|
| `sample_images/bell_pepper.jpg` | 13870 | 279 x 600 | `88a6cfc58176871df8ff1f6661d85dfec60c4aea6a4e5cf8076dd2a6ef1a32c0` |
| `sample_images/cucumber.jpg` | 17467 | 236 x 600 | `3c74bce72aef8b8f72df4dad099c5e97321166b09f2d3060a15aac0d4dcd594d` |
| `sample_images/eggplant.jpg` | 8868 | 102 x 600 | `dd3696cf02dd657bfe1979d33c40664980a97bf95ddc0d1deb5565fa4506676a` |
| `sample_images/zucchini.jpg` | 14575 | 600 x 182 | `89ad8bc9423f74b446c54ccc99d843c70eab81baf53d2218d64a3394c0ec57bb` |
| `SQL lot 1: tomato_1.jpg` | 16230 | 420 x 415 | `63f4a9b47c1176f5f1eca1ca671cc52f692c5e29665a6536c6a4689d20d0cc55` |
| `SQL lot 2: tomato_2.jpg` | 15906 | 399 x 420 | `6352b34a7e73a8b68a0273bbfccb806be15f525bdc5cbf568d49b4125d84a08f` |
| `SQL lot 3: cucumber_1.jpg` | 11612 | 171 x 420 | `6b97166001f94765c7bc8ae88da60b3c8de02618ab01aac1cc65dc8ebef8420d` |
| `SQL lot 4: cucumber_2.jpg` | 11508 | 167 x 420 | `6f6efd140a3051ede18d42329e742242d2aebfc8d7fb9c822caa6357d14f2248` |
| `SQL lot 5: dates_1.jpg` | 5590 | 257 x 140 | `c3e657495721c57035f9ba5ae110cc88e9f25f1c90f8381a1aecd201a267d659` |
| `SQL lot 6: dates_2.jpg` | 5476 | 250 x 128 | `441f740481d2b1563a58c18077c0fed56abc794479bea120b6460bbe31fa8502` |
| `SQL lot 7: pepper_1.jpg` | 8845 | 197 x 420 | `06565cb5e49ea936a6baf8f8e06f973015adc499e25e1e42a21a0f5639893220` |
| `SQL lot 8: tomato_3.jpg` | 16097 | 395 x 420 | `872fd22c9b38aec58d0efd90dd8962710e9a865ab6617cd8eb9473219ca17ed9` |
| `SQL lot 9: eggplant_1.jpg` | 6007 | 93 x 420 | `9660d641c24090253fa4100ab1aab16413780369f020eed294e5bfcdd2f0f5c5` |
| `SQL lot 10: eggplant_2.jpg` | 5873 | 87 x 420 | `065d929a899770a6b5eeaca46f25cd5071d8d90027810de7936076e89f501d1b` |
| `SQL lot 11: zucchini_1.jpg` | 13462 | 420 x 279 | `692e7f73146103e0f0d78987f781995e7dfd61ba75ed6f80def8316106002273` |
| `SQL lot 12: dates_3.jpg` | 5962 | 242 x 140 | `a7d21eec042642d88b106a2bf8cff047d9fefea1482167a65005f76faea64960` |

## Decision needed before packaging

Ask the original package provider for the download/source list, dataset commit/version and transformations. Then record a verified URL and applicable credit/license per image (or a demonstrably common source/version). If that cannot be recovered, Abd Alrahman must decide whether to obtain replacement images with documented provenance and authorize the corresponding SQL/demo-image change and validation. Track B has not replaced images or inferred redistribution clearance. PACKAGE-01 remains blocked on artifact review and this attribution decision.

This attribution record does not license the application code, student work or instructor PDF/PPTX. No blanket project license is introduced.
