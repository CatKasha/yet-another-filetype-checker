import sys
import os.path

def guess_ext(f_path):
    f_size = os.path.getsize(f_path)
    with open(f_path, "rb") as fab:
        buf = fab.read(8)
        buf += b"0" * (8 - len(buf))


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


        # increase buf to 12 bytes
        buf += fab.read(4)
        buf += b"0" * (12 - len(buf))


        # 3GP
        if (buf[4] == 0x66 and
            buf[5] == 0x74 and
            buf[6] == 0x79 and
            buf[7] == 0x70 and
            buf[8] == 0x33 and
            buf[9] == 0x67 and
            buf[10] == 0x70):
            return "3gp"


        # ID3v2 tag skip'er
        # reference:
        # http://id3.org/id3v2.4.0-structure (via Wayback Machine)
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


        # EBML, part of MKV and WEBM
        # references:
        # https://matroska.sourceforge.net/technical/specs/index.html
        # https://www.webmproject.org/docs/container/
        # https://yoooonghyun.gitbook.io/documents/multimedia/containers/webm
        if (buf[0] == 0x1A and
            buf[1] == 0x45 and
            buf[2] == 0xDF and
            buf[3] == 0xA3):
            another_buf = bin(buf[4])[2:].zfill(8)
            len_ebml_header_data_size = 0
            for i in range(len(another_buf)):
                if ("1" == another_buf[i]):
                    len_ebml_header_data_size = i + 1
                    break

            # seems every element in EBML header have fixed size except DocType
            # jump straight to DocType and check whats there
            # EBML header + length of EBML header data size + 4 * 4b (2b element ID + 1b data length + 1b data)
            fab.seek(4 + len_ebml_header_data_size + 16, 0)
            buf = fab.read(11)
            buf += b"0" * (11 - len(buf))

            if (buf == bytearray([0x42, 0x82, 0x88, 0x6D, 0x61, 0x74, 0x72, 0x6F, 0x73, 0x6B, 0x61])):
                return "mkv"
            if (buf[:7] == bytearray([0x42, 0x82, 0x84, 0x77, 0x65, 0x62, 0x6D])):
                return "webm"


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
