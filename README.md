# SCN to OME-TIFF

Convert a Leica .SCN file to OME-TIFF format.

Usage:
```python scn2ometiff.py input.scn output.ome.tif```

Requirements:
* tifffile
* tqdm
* zarr

## Caveats

* This script is very simplistic and makes some assumptions about how the
  .scnfile is organized. If it doesn't work properly on your image please file
  an issue.

* The image data undergoes a second round of lossy JPEG compression during
  conversion (the first round being the original compression in the .scn
  file). There is no visible change in image quality but the pixel values will
  be slightly slightly different than those in the original image.

* Minimal metadata is copied. Currently only core image metadata and pixel
  physical dimensions are included in the output OME-TIFF.

* The macro overview image is not copied. If this would be useful for your use
  case, please file an issue.
