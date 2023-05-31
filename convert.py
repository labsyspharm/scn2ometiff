import sys
import tifffile
import tqdm
import uuid
import zarr

in_path, out_path = sys.argv[1:3]

tiff = tifffile.TiffFile(in_path)
series = tiff.series[1]
plane = series[0]
pyramid = zarr.open(series.aszarr())

def tiles(zimg):
    th, tw = zimg.chunks[:2]
    ch, cw = zimg.cdata_shape[:2]
    for j in range(ch):
        for i in range(cw):
            yield zimg[th * j : th * (j + 1), tw * i : tw * (i + 1)]

def progress(zimg, level):
    ch, cw = zimg.cdata_shape[:2]
    total = ch * cw
    t = tqdm.tqdm(tiles(zimg), desc=f"Level {level}", total=total)
    # Fix issue with tifffile's peek_iterator causing a missed update.
    t.update()
    return iter(t)

with tifffile.TiffWriter(out_path, ome=True, bigtiff=True) as writer:
    writer.write(
        data=progress(pyramid[0], 1),
        shape=pyramid[0].shape,
        subifds=len(pyramid) - 1,
        dtype=pyramid[0].dtype,
        tile=pyramid[0].chunks[:2],
        resolution=plane.resolution + (plane.resolutionunit,),
        compression="jpeg",
        metadata={"UUID": uuid.uuid4().urn},
    )
    for level in range(1, len(pyramid)):
        zimg = pyramid[level]
        writer.write(
            data=progress(zimg, level + 1),
            shape=zimg.shape,
            subfiletype=1,
            dtype=zimg.dtype,
            tile=zimg.chunks[:2],
            compression="jpeg",
        )
