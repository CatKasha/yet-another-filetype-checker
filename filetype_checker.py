import sys
import os.path

def guess_ext(f_path):
    f_size = os.path.getsize(f_path)
    with open(f_path, "rb") as fab:
        buf = fab.read(8)
        buf += b"\x00" * (8 - len(buf))


        # JPEG XR
        # reference:
        # https://www.itu.int/rec/T-REC-T.832-201906-I/en
        if (buf[0] == 0x49 and
            buf[1] == 0x49 and
            buf[2] == 0xBC and
            buf[3] == 0x01):
            return "jxr"


        # TIFF
        # reference:
        # https://web.archive.org/web/20210108174645/https://www.adobe.io/content/dam/udp/en/open/standards/tiff/TIFF6.pdf
        if (buf[0] == 0x49 and
            buf[1] == 0x49 and
            buf[2] == 0x2A and
            buf[3] == 0x00 or
            buf[0] == 0x4D and
            buf[1] == 0x4D and
            buf[2] == 0x00 and
            buf[3] == 0x2A):
            return "tif"


        # PSD and PSB
        # reference:
        # https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/
        if (buf[0] == 0x38 and
            buf[1] == 0x42 and
            buf[2] == 0x50 and
            buf[3] == 0x53 and
            buf[4] == 0x00):
            if (buf[5] == 0x01):
                return "psd"
            
            if (buf[5] == 0x02):
                return "psb"


        # DDS
        # reference:
        # https://en.wikipedia.org/wiki/DirectDraw_Surface
        # http://fileformats.archiveteam.org/wiki/DDS
        if (buf[0] == 0x44 and
            buf[1] == 0x44 and
            buf[2] == 0x53 and
            buf[3] == 0x20):
            return "dds"


        # WOFF and WOFF2
        # reference:
        # https://www.w3.org/TR/WOFF/#appendix-b
        # https://www.w3.org/TR/WOFF2/#IMT
        if (buf[0] == 0x77 and
            buf[1] == 0x4F and
            buf[2] == 0x46):
            if (buf[3] == 0x46):
                return "woff"

            if (buf[3] == 0x32):
                return "woff2"


        # ICO and CUR
        # reference:
        # https://en.wikipedia.org/wiki/ICO_(file_format)#Header
        if (buf[0] == 0x00 and
            buf[1] == 0x00 and
            buf[3] == 0x00):
            if (buf[2] == 0x01):
                return "ico"

            if (buf[2] == 0x02):
                return "cur"


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
        # reference:
        # https://py7zr.readthedocs.io/en/v0.20.5/archive_format.html#signature-header
        if (buf[0] == 0x37 and
            buf[1] == 0x7A and
            buf[2] == 0xBC and
            buf[3] == 0xAF and
            buf[4] == 0x27 and
            buf[5] == 0x1C):
            another_buf = buf + fab.read(24)
            fab.seek(8, 0)

            header_db_offset = int.from_bytes(another_buf[12:20], byteorder="little")
            header_db_size = int.from_bytes(another_buf[20:28], byteorder="little")

            if (f_size == 32 + header_db_offset + header_db_size):
                return "7z"
            # else:
            #    return "7z.001"


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
        # reference:
        # https://www.w3.org/Graphics/GIF/spec-gif87.txt
        # https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        if (buf[0] == 0x47 and
            buf[1] == 0x49 and
            buf[2] == 0x46 and
            buf[3] == 0x38 and
           (buf[4] == 0x37 or buf[4] == 0x39) and
            buf[5] == 0x61):
            return "gif"


        # JIF
        # reference:
        # https://web.archive.org/web/20010603113404/http://jeff.cafe.net/jif/
        if (buf[0] == 0x4A and
            buf[1] == 0x49 and
            buf[2] == 0x46 and
            buf[3] == 0x39 and
            buf[4] == 0x39 and
            buf[5] == 0x61):
            return "jif"


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
            # reference:
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

            major_brand = ftyp_data[0:4].decode("ascii", errors="ignore")
            # ftyp_version = int.from_bytes(buf[4:8], byteorder="big")
            compatible_brands = []
            for i in range(8, ftyp_size - 8, 4):
                compatible_brands.append(ftyp_data[i : i + 4].decode("ascii", errors="ignore"))


            # MOV
            if (major_brand == "qt  "):
                return "mov"


            # AVIF
            # reference:
            # https://aomediacodec.github.io/av1-avif/v1.1.0.html#brands
            if (major_brand == "avif" or major_brand == "avis"):
                return "avif"


            # HEIC
            # reference:
            # https://nokiatech.github.io/heif/technical.html
            if (major_brand == "heic"):
                return "heic"


            # MP4
            if (major_brand in ["isom", "iso2", "iso3", "iso4", "iso5", "iso6", "iso7", "iso8", "iso9", "mp42", "avc1"]):
                return "mp4"

            if (major_brand == "M4V " and ("M4V " in compatible_brands) == False):
                if ("mp42" in compatible_brands):
                    return "mp4"


            # M4V
            if (major_brand in ["M4V ", "M4VP", "M4VH"]):
                if (major_brand in compatible_brands):
                    return "m4v"


            # 3GP
            # reference:
            # https://www.etsi.org/deliver/etsi_ts/126200_126299/126244/17.00.00_60/ts_126244v170000p.pdf
            if (major_brand == "3gp4" and "3gp4" in compatible_brands):
                return "3gp"

            # 3gh9 is not in this list
            three_gp_brands = ["3gp5", "3gp6", "3gp7", "3gp8",
                               "3gr6",
                               "3gs6",
                               "3ge7",
                               "3gg6",
                               "3gt8", "3gt9"]

            if (major_brand in three_gp_brands):
                if (major_brand in compatible_brands):
                    req_brands = ["isom", "avc1", "iso2"]
                    for brand in req_brands:
                        if (brand in compatible_brands):
                            return "3gp"


            # 3G2
            # reference:
            # https://web.archive.org/web/20091007071048/http://www.3gpp2.org/Public_html/specs/C.S0050-B_v1.0_070521.pdf
            if (major_brand in ["3g2a", "3g2b", "3g2c"]):
                if (major_brand in compatible_brands):
                    return "3g2"


        # ZIP something
        if (buf[0] == 0x50 and
            buf[1] == 0x4B and
            buf[2] == 0x03 and
            buf[3] == 0x04):
            # EPUB
            # reference:
            # https://www.w3.org/TR/epub/#app-media-type
            fab.seek(30, 0)
            if (fab.read(28) == b"mimetypeapplication/epub+zip"):
                return "epub"
            fab.seek(8,0)


        # increase buf to 12 bytes
        buf += fab.read(4)
        buf += b"\x00" * (12 - len(buf))


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
            buf_after_id3 += b"\x00" * (4 - len(buf_after_id3))

            fab.seek(12, 0)


        # MP3
        # reference:
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
        # reference:
        # https://matroska.sourceforge.net/technical/specs/index.html
        # https://www.webmproject.org/docs/container/
        # https://yoooonghyun.gitbook.io/documents/multimedia/containers/webm
        if (buf[0] == 0x1A and
            buf[1] == 0x45 and
            buf[2] == 0xDF and
            buf[3] == 0xA3):
            another_buf = buf
            def parce_data_size(init_pos):
                first_byte = bin(another_buf[init_pos])[2:].zfill(8)
                data_size_len = 0
                for i in range(len(first_byte)):
                    if ("1" == first_byte[i]):
                        data_size_len = i + 1
                        break

                data_size = first_byte[data_size_len:]
                for i in range(data_size_len - 1):
                    data_size += bin(another_buf[init_pos + 1 + i])[2:].zfill(8)

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
            if (doctype_data == "matroska"):
                return "mkv"

            # WEBM
            if (doctype_data == "webm"):
                return "webm"


        # RIFF reader
        if (buf[0] == 0x52 and
            buf[1] == 0x49 and
            buf[2] == 0x46 and
            buf[3] == 0x46):
            format_type = buf[8:12].decode("ascii", errors="ignore")

            # WEBP
            # reference:
            # https://developers.google.com/speed/webp/docs/riff_container?hl=en#webp_file_header
            if (format_type == "WEBP"):
                return "webp"

            # AVI
            # reference:
            # https://learn.microsoft.com/en-us/windows/win32/directshow/avi-riff-file-reference
            if (format_type == "AVI "):
                return "avi"

            # WAV
            # reference:
            # https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
            if (format_type == "WAVE"):
                return "wav"

            # ANI
            # reference:
            # http://fileformats.archiveteam.org/wiki/Windows_Animated_Cursor
            if (format_type == "ACON"):
                return "ani"


        # MPEG-TS
        # reference:
        # https://en.wikipedia.org/wiki/MPEG_transport_stream#Packet
        if (buf[0] == 0x47):
            if (f_size > 188):
                fab.seek(1, 0)
                # check another 4 times for sync byte
                for i in range(2, 6):
                    if (f_size > 188 * i):
                        fab.seek(187, 1)
                        another_buf = fab.read(1)
                        if (another_buf != b"\x47"):
                            break
                    else:
                        break
                else:
                    return "ts"

                fab.seek(12, 0)


        # BitTorrent metainfo file
        # reference:
        # https://www.bittorrent.org/beps/bep_0003.html
        if (buf[0] == 0x64 and
            buf[1] == 0x38 and
            buf[2] == 0x3A and
            buf[3] == 0x61 and
            buf[4] == 0x6E and
            buf[5] == 0x6E and
            buf[6] == 0x6F and
            buf[7] == 0x75 and
            buf[8] == 0x6E and
            buf[9] == 0x63 and
            buf[10] == 0x65):
            return "torrent"


        # JPEG XL
        # reference:
        # https://github.com/libjxl/libjxl/blob/main/doc/format_overview.md#file-format
        if (buf[0] == 0xFF and
            buf[1] == 0x0A or
            buf[0] == 0x00 and
            buf[1] == 0x00 and
            buf[2] == 0x00 and
            buf[3] == 0x0C and
            buf[4] == 0x4A and
            buf[5] == 0x58 and
            buf[6] == 0x4C and
            buf[7] == 0x20 and
            buf[8] == 0x0D and
            buf[9] == 0x0A and
            buf[10] == 0x87 and
            buf[11] == 0x0A):
            return "jxl"


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
