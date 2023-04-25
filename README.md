# yet another filetype checker

kinda similar to [filetype.py](https://github.com/h2non/filetype.py) but:
- only reads first 8 bytes and reads more if needed
- everything in single file
- only output file extension (maybe i will add MIME type output too, idk)
- only works with files (not with bytearray and other stuff)

## supported formats
- 7z
- pdf
- jpg
- gif
- png
- apng
- qoi
- bmp
- mov
- 3gp
- mp3
- flac
- mkv
- webm

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