import sys
import os.path

def guess_ext(f_path):
    f_size = os.path.getsize(f_path)
    with open(f_path, "rb") as fab:
        buf = fab.read(8)
        buf += b"0" * (8 - len(buf))


        # SWF
        # reference:
        # https://web.archive.org/web/20130202203813/http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/swf/pdf/swf-file-format-spec.pdf
        if ((buf[0] == 0x46 or
             buf[0] == 0x43 or
             buf[0] == 0x5A) and
            buf[1] == 0x57 and
            buf[2] == 0x53):
            return "swf"


        # 7z
        if (buf[0] == 0x37 and
            buf[1] == 0x7A and
            buf[2] == 0xBC and
            buf[3] == 0xAF and
            buf[4] == 0x27 and
            buf[5] == 0x1C):
            return "7z"


        # PDF
        if (buf[0] == 0x25 and
            buf[1] == 0x50 and
            buf[2] == 0x44 and
            buf[3] == 0x46 and
            buf[4] == 0x2D):
            return "pdf"


        # JPEG
        if (buf[0] == 0xFF and
            buf[1] == 0xD8 and
            buf[2] == 0xFF):
            return "jpg"


        # GIF
        if (buf[0] == 0x47 and
            buf[1] == 0x49 and
            buf[2] == 0x46 and
            buf[3] == 0x38 and
           (buf[4] == 0x37 or buf[4] == 0x39) and
            buf[5] == 0x61):
            return "gif"


        # PNG
        if (buf[0] == 0x89 and
            buf[1] == 0x50 and
            buf[2] == 0x4E and
            buf[3] == 0x47 and
            buf[4] == 0x0D and
            buf[5] == 0x0A and
            buf[6] == 0x1A and
            buf[7] == 0x0A):

            # APNG
            # references:
            # https://wiki.mozilla.org/APNG_Specification#Structure
            # http://www.libpng.org/pub/png/spec/1.2/PNG-Structure.html
            while (f_size > fab.tell()):
                buf = fab.read(8)

                data_length = int.from_bytes(buf[0:4], byteorder="big")
                chunk_type = buf[4:8].decode("ascii", errors="ignore")

                # acTL chunk in APNG must appear before IDAT
                # IEND is end of file
                if (chunk_type == "IDAT" or chunk_type == "IEND"):
                    return "png"
                if (chunk_type == "acTL"):
                    return "apng"

                # move to the next chunk by skipping chunk data and crc (4 bytes)
                fab.seek(data_length + 4, 1)
            return "png"


        # QOI
        if (buf[0] == 0x71 and
            buf[1] == 0x6F and
            buf[2] == 0x69 and
            buf[3] == 0x66):
            return "qoi"


        # BMP
        if (buf[0] == 0x42 and
            buf[1] == 0x4D):
            return "bmp"


        # ftyp reader
        # reference:
        # https://ftyps.com/what.html
        if (buf[4] == 0x66 and
            buf[5] == 0x74 and
            buf[6] == 0x79 and
            buf[7] == 0x70):
            ftyp_size = int.from_bytes(buf[0:4], byteorder="big")

            ftyp_data = fab.read(ftyp_size - 8)
            fab.seek(8, 0)

            ftyp_major = ftyp_data[0:4].decode("ascii", errors="ignore")
            # ftyp_version = int.from_bytes(buf[4:8], byteorder="big")
            # ftyp_compat = []
            # for i in range(8, ftyp_size - 8, 4):
            #     ftyp_compat.append(ftyp_data[i : i + 4].decode("ascii", errors="ignore"))

            # MOV
            if (ftyp_major == "qt  "):
                return "mov"

            # AVIF
            if (ftyp_major == "avif"):
                return "avif"

            # disabled until i figured out how to properly detect this format

            # 3GP
            # if (ftyp_major[0:3] == "3gp"):
            #     return "3gp"

            # 3G2
            # if (ftyp_major[0:3] == "3g2"):
            #     return "3g2"


        # increase buf to 12 bytes
        buf += fab.read(4)
        buf += b"0" * (12 - len(buf))


        # ID3v2 tag skip'er
        # reference:
        # https://web.archive.org/web/20070609163800/http://www.id3.org/id3v2.4.0-structure
        buf_after_id3 = buf
        if (buf[0] == 0x49 and
            buf[1] == 0x44 and
            buf[2] == 0x33):

            id3_flags = bin(buf[5])[2:].zfill(8)
            footer_present = bool(int(id3_flags[3]))
            id3_tag_size = ""
            for i in buf[6:10]:
                id3_tag_size += bin(i)[2:].zfill(7)

            id3_tag_size = int(id3_tag_size, 2) + 10
            if (footer_present):
                id3_tag_size += 10

            fab.seek(id3_tag_size, 0)

            buf_after_id3 = fab.read(4)
            buf_after_id3 += b"0" * (4 - len(buf_after_id3))

            fab.seek(12, 0)


        # MP3
        # references:
        # https://www.datavoyage.com/mpgscript/mpeghdr.htm
        # https://en.wikipedia.org/wiki/MP3#/media/File:Mp3filestructure.svg
        if (buf_after_id3[0] == 0xFF):
            if (buf_after_id3[1] == 0xE2 or  # MPEG 2.5 with error protection
                buf_after_id3[1] == 0xE3 or  # MPEG 2.5 w/o error protection
                buf_after_id3[1] == 0xF2 or  # MPEG 2 with error protection
                buf_after_id3[1] == 0xF3 or  # MPEG 2 w/o error protection
                buf_after_id3[1] == 0xFA or  # MPEG 1 with error protection
                buf_after_id3[1] == 0xFB):   # MPEG 1 w/o error protection
                return "mp3"


        # FLAC
        if (buf_after_id3[0] == 0x66 and
            buf_after_id3[1] == 0x4C and
            buf_after_id3[2] == 0x61 and
            buf_after_id3[3] == 0x43):
            return "flac"


        # EBML reader
        # references:
        # https://matroska.sourceforge.net/technical/specs/index.html
        # https://www.webmproject.org/docs/container/
        # https://yoooonghyun.gitbook.io/documents/multimedia/containers/webm
        if (buf[0] == 0x1A and
            buf[1] == 0x45 and
            buf[2] == 0xDF and
            buf[3] == 0xA3):
            def parce_data_size(init_pos):
                another_buf = bin(buf[init_pos])[2:].zfill(8)
                data_size_len = 0
                for i in range(len(another_buf)):
                    if ("1" == another_buf[i]):
                        data_size_len = i + 1
                        break

                data_size = another_buf[data_size_len:]
                for i in range(data_size_len - 1):
                    data_size += bin(buf[init_pos + 1 + i])[2:].zfill(8)

                return data_size_len, int(data_size, 2)

            ebml_header_data_size_len, ebml_header_data_size = parce_data_size(4)

            fab.seek(4 + ebml_header_data_size_len, 0)
            another_buf = fab.read(ebml_header_data_size)
            fab.seek(12, 0)

            doctype_index = another_buf.find(b"\x42\x82") + 2
            doctype_data_size_len, doctype_data_size = parce_data_size(doctype_index)
            doctype_data = another_buf[doctype_index + doctype_data_size_len : doctype_index + doctype_data_size_len + doctype_data_size]

            doctype_data = doctype_data.decode("ascii", errors="ignore")

            # MKV
            if ("matroska" in doctype_data):
                return "mkv"

            # WEBM
            if ("webm" in doctype_data):
                return "webm"


        # RIFF reader
        # references:
        # https://developers.google.com/speed/webp/docs/riff_container?hl=en#riff_file_format
        # https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
        # https://learn.microsoft.com/en-us/windows/win32/directshow/avi-riff-file-reference
        if (buf[0] == 0x52 and
            buf[1] == 0x49 and
            buf[2] == 0x46 and
            buf[3] == 0x46):
            format_type = buf[8:12].decode("ascii", errors="ignore")

            # WEBP
            if(format_type == "WEBP"):
                return "webp"

            # AVI
            if(format_type == "AVI "):
                return "avi"

            # WAV
            if(format_type == "WAVE"):
                return "wav"


        # there no other matcher, return None
        return None


def main():
    if (len(sys.argv) < 2):
        sys.exit("file path not given")

    file_path = sys.argv[1]
    if (os.path.isfile(file_path)):
        print(guess_ext(file_path))
    else:
        sys.exit("given path is not a file")


if (__name__ == "__main__"):
    main()
