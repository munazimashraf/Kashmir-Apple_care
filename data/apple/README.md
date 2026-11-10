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
