import sys
import os.path

def guess_ext(f_path):
    f_size = os.path.getsize(f_path)
    with open(f_path, "rb") as fab:
        buf = fab.read(8)


        # GIF
        if (buf[0] == 0x47 and
            buf[1] == 0x49 and
            buf[2] == 0x46):
            # 87a or 89a
            if ((buf[3] == 0x38 and
                 buf[4] == 0x37 and
                 buf[5] == 0x61)
                 or
                (buf[3] == 0x38 and
                 buf[4] == 0x39 and
                 buf[5] == 0x61)):
                return "gif"


        # PNG
        if (buf[0] == 0x89 and
            buf[1] == 0x50 and
            buf[2] == 0x4e and
            buf[3] == 0x47 and
            buf[4] == 0x0d and
            buf[5] == 0x0a and
            buf[6] == 0x1a and
            buf[7] == 0x0a):

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


        # MP3
        # references:
        # https://www.datavoyage.com/mpgscript/mpeghdr.htm
        # https://en.wikipedia.org/wiki/MP3#/media/File:Mp3filestructure.svg
        if (buf[0] == 0xFF):
            if (buf[1] == 0xE2 or  # MPEG 2.5 with error protection
                buf[1] == 0xE3 or  # MPEG 2.5 w/o error protection
                buf[1] == 0xF2 or  # MPEG 2 with error protection
                buf[1] == 0xF3 or  # MPEG 2 w/o error protection
                buf[1] == 0xFA or  # MPEG 1 with error protection
                buf[1] == 0xFB):   # MPEG 1 w/o error protection
                return "mp3"

        if (buf[0] == 0x49 and
            buf[1] == 0x44 and
            buf[2] == 0x33):
            return "mp3"

            # NOTE according to https://www.garykessler.net/library/file_sigs.html
            # there a .koz format that uses same ID3 header, but i cant find that file online
            # so check MP3 header after ID3 chunk?
            # half done ID3 chunk size reader
            #
            # buf += fab.read(2)
            # buf_2 = ""
            # for i in buf[6:10]:
            #     buf_2 += bin(i)[2:].zfill(7)
            # buf_2 = int(buf_2, 2) + 10


        # QOI
        if (buf[0] == 0x71 and
            buf[1] == 0x6F and
            buf[2] == 0x69 and
            buf[3] == 0x66):
            return "qoi"


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
