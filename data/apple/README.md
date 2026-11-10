# Apple leaf dataset contract

Place licensed PlantVillage Apple images and Kashmir field images in:

```text
data/apple/
  train/{apple_scab,alternaria_leaf_blotch,powdery_mildew,black_rot,cedar_apple_rust,european_red_mite,healthy}/
  val/{same class directories}/
  test/{same class directories}/
```

Keep orchard blocks separated between splits to avoid leakage. Do not include
images for which the project does not have redistribution rights.

The current local dataset combines the Apple PlantVillage subset with the
public Kaggle D-KAP dataset (`hsmcaju/d-kap`) and the supplied archive
`drive-download-20261110T053804Z-1-001.zip`. The supplied archive contributes
Apple Scab, Black Rot, Cedar Apple Rust, and Healthy images. Its images are
split deterministically 80% train, 10% validation, and 10% test by filename
hash; this keeps the split reproducible, but source-level duplicate checks are
still recommended.

D-KAP's `LEAF BLOTCH` class is stored as `alternaria_leaf_blotch`; verify this
label with an agricultural expert before treating it as Kashmir-specific
ground truth.

The combined dataset currently has six classes. Genuine apple images for
`european_red_mite` are still required before running the seven-class training
script. The indigenous dataset archive is extracted at
`Downloads/indigenous-apple-leaf-dataset`; its Apple Mosaic class is retained
there but intentionally excluded from the classifier because it is not one of
the configured classes. The ICAR-CITH archive is extracted at
`Downloads/icar-cith-apple-dataset`; its Alternaria and Powdery Mildew folders
are included, while Apple Mosaic and the additional Scab folder are excluded.

The supplied archive does not contain Alternaria Leaf Blotch, Powdery Mildew,
or European Red Mite. Run the seven-class training command only after those
classes are present. For a four-class experiment using only the supplied
archive, pass `--classes apple_scab black_rot cedar_apple_rust healthy` and
write to a separate output directory so the production six/seven-class
artifact is not overwritten.
