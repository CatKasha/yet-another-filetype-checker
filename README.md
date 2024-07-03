# yet another filetype checker

kinda similar to [filetype.py](https://github.com/h2non/filetype.py) but:
- at first reads 8 bytes and reads more if needed
- - [python will use optimal read chunk size automatically anyway](https://docs.python.org/3/library/functions.html#open)
- everything in single file
- only output file extension (maybe i will add MIME type output too, idk)
- only works with files (not with bytearray and other stuff)

## supported formats
- jxr
- tif
- psd
- psb
- dds
- woff
- woff2
- ico
- cur
- swf
- 7z (only non splitted archive)
- pdf
- jpg
- gif
- jif
- png
- apng
- qoi
- bmp
- mov
- avif
- heic
- mp4
- m4v
- 3gp
- 3g2
- epub
- mp3
- flac
- mkv
- webm
- webp
- avi
- wav
- ani
- ts
- torrent
- jxl
- html
- blank (fake extention, file filled with zeros/null bytes)

## how to use
as standalone app:
```shell
.\filetype_checker.py sample.png
apng
```

as library:
```python
import os.path
import filetype_checker

file_path = "sample.png"

if (os.path.isfile(file_path)):
    # if extension was not found it will return None
    file_extension = filetype_checker.guess_ext(file_path)
    
    if (file_extension):
        print("File extension:", file_extension)
    else:
        print("Cant guess file extension")
else:
    print("Given path is not a file")
```