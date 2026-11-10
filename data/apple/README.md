# Apple leaf dataset contract

Place licensed PlantVillage Apple images and Kashmir field images in:

```text
data/apple/
  train/{apple_scab,alternaria_leaf_blotch,powdery_mildew,black_rot,cedar_apple_rust,healthy}/
  val/{same class directories}/
  test/{same class directories}/
```

Keep orchard blocks separated between splits to avoid leakage. Do not include
images for which the project does not have redistribution rights.

The supplied six-class archives can be prepared without committing raw images:

```bash
python ml/prepare_apple_dataset.py \
  --primary-zip "/path/to/drive-download-20261110T053804Z-1-001.zip" \
  --icar-zip "/path/to/Apple Diseases Images.zip" \
  --output-dir "/path/to/applecare-dataset"
python ml/train_apple_model.py \
  --data-dir "/path/to/applecare-dataset" \
  --output-dir artifacts/applecare
```

The ICAR archive is nested inside its downloaded ZIP; pass the extracted
`Apple Diseases Images.zip` to `--icar-zip`. Raw datasets should remain outside
the repository.
