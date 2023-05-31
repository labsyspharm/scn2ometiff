import argparse
import tifffile
import tqdm
import uuid
import zarr

def tiles(zimg):
    th, tw = zimg.chunks[:2]
    ch, cw = zimg.cdata_shape[:2]
    for j in range(ch):
        for i in range(cw):
            yield zimg[th * j : th * (j + 1), tw * i : tw * (i + 1)]

def progress(zimg, level):
    ch, cw = zimg.cdata_shape[:2]
    total = ch * cw
    t = tqdm.tqdm(tiles(zimg), desc=f"  Level {level}", total=total)
    # Fix issue with tifffile's peek_iterator causing a missed update.
    t.update()
    return iter(t)

parser = argparse.ArgumentParser(
    description="Convert a Leica .SCN image to OME-TIFF format.",
)
parser.add_argument(
    "input", help="Path to input image", metavar="input.scn"
)
parser.add_argument(
    "output", help="Path to output image", metavar="output.ome.tif"
)
args = parser.parse_args()

tiff = tifffile.TiffFile(args.input)

with tifffile.TiffWriter(args.output, ome=True, bigtiff=True) as writer:
    num_images = len(tiff.series) - 1
    for i, series in enumerate(tiff.series[1:], 1):
        print(f"Image {i}/{num_images} ({series.name})")
        plane = series[0]
        pyramid = zarr.open(series.aszarr())
        writer.write(
            data=progress(pyramid[0], 1),
            shape=pyramid[0].shape,
            subifds=len(pyramid) - 1,
            dtype=pyramid[0].dtype,
            tile=pyramid[0].chunks[:2],
            resolution=plane.resolution + (plane.resolutionunit,),
            compression="jpeg",
            metadata={"UUID": uuid.uuid4().urn, "Name": series.name},
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
        print()
