"""Dependency-free BMP batch resizing for reproducible image jobs.

Only uncompressed 24-bit BMP files are supported; source files are never modified.
"""
import struct
from pathlib import Path
from meshcompute.common.errors import TaskExecutionError
from meshcompute.common.settings import get_settings
from meshcompute.worker.handlers.base import JsonObject
from meshcompute.worker.handlers.word_count import resolve_input

MAX_IMAGE_EDGE=4096
def _read_bmp(path: Path):
    """Decode a bounded, uncompressed 24-bit BMP into top-down BGR pixels."""
    raw=path.read_bytes()
    if len(raw)<54 or raw[:2]!=b"BM": raise TaskExecutionError("expected a valid BMP file")
    pixel_offset=struct.unpack_from("<I",raw,10)[0]
    header_size=struct.unpack_from("<I",raw,14)[0]
    width,height=struct.unpack_from("<ii",raw,18)
    planes,bits,compression=struct.unpack_from("<HHI",raw,26)
    if header_size<40 or planes!=1 or bits!=24 or compression!=0:
        raise TaskExecutionError("image_resize supports uncompressed 24-bit BMP files only")
    if width<=0 or height==0 or abs(height)>MAX_IMAGE_EDGE or width>MAX_IMAGE_EDGE:
        raise TaskExecutionError("BMP dimensions are invalid or exceed the safe edge limit")
    stride=((width*3+3)//4)*4
    if pixel_offset+stride*abs(height)>len(raw): raise TaskExecutionError("BMP pixel data is truncated")
    pixels=[]
    for output_y in range(abs(height)):
        source_y=output_y if height<0 else abs(height)-1-output_y
        row=raw[pixel_offset+source_y*stride:pixel_offset+(source_y+1)*stride]
        pixels.append([row[x*3:x*3+3] for x in range(width)])
    return width,abs(height),pixels
def _write_bmp(path: Path,width: int,height: int,pixels: list[list[bytes]]) -> int:
    """Write BGR pixels using the Windows 3.x BMP header format."""
    stride=((width*3+3)//4)*4;pixel_size=stride*height
    header=struct.pack("<2sIHHI",b"BM",54+pixel_size,0,0,54)
    dib=struct.pack("<IiiHHIIiiII",40,width,height,1,24,0,pixel_size,2835,2835,0,0)
    padding=b"\x00"*(stride-width*3)
    with path.open("wb") as output:
        output.write(header);output.write(dib)
        for row in reversed(pixels): output.write(b"".join(row)+padding)
    return path.stat().st_size

class ImageResizeHandler:
    """Resize only explicitly named shared-volume BMP images."""
    def split(self,input_ref: str,options: JsonObject) -> list[JsonObject]:
        """List supported source images and partition them into bounded batches."""
        folder=resolve_input(input_ref)
        if not folder.is_dir(): raise TaskExecutionError("image_resize input_ref must name a shared data directory")
        batch_size=max(1,min(100,int(options.get("batch_size",8))))
        images=sorted(path for path in folder.glob("*.bmp") if path.is_file())
        if not images: raise TaskExecutionError("no BMP images found in the input directory")
        names=[path.relative_to(get_settings().data_dir.resolve()).as_posix() for path in images]
        return [{"image_paths":names[index:index+batch_size],"width":int(options.get("width",256)),
                 "height":int(options.get("height",256)),"output_dir":str(options.get("output_dir","output/images"))}
                for index in range(0,len(names),batch_size)]
    def execute(self,payload: JsonObject) -> JsonObject:
        """Resize one batch using nearest-neighbor sampling without external libraries."""
        width=int(payload["width"]);height=int(payload["height"])
        if not 1<=width<=MAX_IMAGE_EDGE or not 1<=height<=MAX_IMAGE_EDGE:
            raise TaskExecutionError(f"target dimensions must be within 1..{MAX_IMAGE_EDGE}")
        output_dir=resolve_input(str(payload["output_dir"]));output_dir.mkdir(parents=True,exist_ok=True)
        completed=[]
        for raw_path in payload["image_paths"]:
            source=resolve_input(str(raw_path));src_width,src_height,pixels=_read_bmp(source)
            resized=[[pixels[min(src_height-1,y*src_height//height)][min(src_width-1,x*src_width//width)]
                      for x in range(width)] for y in range(height)]
            destination=output_dir/f"{source.stem}_{width}x{height}.bmp"
            size=_write_bmp(destination,width,height,resized)
            completed.append({"source":str(raw_path),"output":str(destination),"bytes":size})
        return {"files":completed}
    def merge(self,results: list[JsonObject]) -> JsonObject:
        """Combine output file descriptors from completed batches."""
        files=[item for result in results for item in result.get("files",[]) if isinstance(item,dict)]
        return {"image_count":len(files),"files":files}
