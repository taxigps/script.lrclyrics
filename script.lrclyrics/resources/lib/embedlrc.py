import os
from tagger import *

def getEmbedLyrics(filename):
    lyrics = getLyrics3(filename)
    if (not lyrics):
        lyrics = getID3Lyrics(filename)
    return lyrics

"""
Get LRC lyrics embed with Lyrics3/Lyrics3V2 format
See: http://id3.org/Lyrics3
     http://id3.org/Lyrics3v2
"""
def getLyrics3(filename):
    f = file(filename, "r")
    f.seek(-128-9, os.SEEK_END)
    buf = f.read(9)
    if (buf != "LYRICS200" and buf != "LYRICSEND"):
        f.seek(-9, os.SEEK_END)
        buf = f.read(9)
    if (buf == "LYRICSEND"):
        """ Find Lyrics3v1 """
        f.seek(-5100-9-11, os.SEEK_CUR)
        buf = f.read(5100+11)
        f.close();
        start = buf.find("LYRICSBEGIN")
        return buf[start+11:]
    elif (buf == "LYRICS200"):
        """ Find Lyrics3v2 """
        f.seek(-9-6, os.SEEK_CUR)
        size = int(f.read(6))
        f.seek(-size-6, os.SEEK_CUR)
        buf = f.read(11)
        if(buf == "LYRICSBEGIN"):
            buf = f.read(size-11)
            tags=[]
            while buf!= '':
                tag = buf[:3]
                length = int(buf[3:8])
                content = buf[8:8+length]
                if (tag == 'LYR'):
                    return content
                buf = buf[8+length:]
    f.close();
    return None

def endOfString(string, utf16=False):
    if (utf16):
        pos = 0
        while True:
            pos += string[pos:].find('\x00\x00') + 1
            if (pos % 2 == 1):
                return pos - 1
    else:
        return string.find('\x00')

def ms2timestamp(ms):
    mins = "0%s" % int(ms/1000/60)
    sec = "0%s" % int((ms/1000)%60)
    msec = "0%s" % int((ms%1000)/10)
    timestamp = "[%s:%s.%s]" % (mins[-2:],sec[-2:],msec[-2:])
    return timestamp

"""
Get SYLT/TXXX lyrics embed with ID3v2 format
See: http://id3.org/id3v2.3.0
"""
def getID3Lyrics(filename):
    id3 = ID3v2(filename)
    if id3.version == 2.2:
        sylt="SLT"
    else:
        sylt="SYLT"
    for tag in id3.frames:
        if tag.fid == sylt:
            enc = ['latin_1','utf_16','utf_16_be','utf_8'][ord(tag.rawdata[0])]
            lang = tag.rawdata[1:4]
            format = tag.rawdata[4]
            ctype = tag.rawdata[5]
            raw = tag.rawdata[6:]
            utf16 = bool(enc.find('16') != -1)
            pos = endOfString(raw, utf16)
            desc = raw[:pos]
            if utf16:
                pos += 1
            content = raw[pos+1:]
            del raw
            lyrics = ""
            while content != "":
                pos = endOfString(content, utf16)
                text = content[:pos].decode(enc)
                if utf16:
                    pos += 1
                time = content[pos+1:pos+5]
                timems = 0
                for x in range(4):
                    timems += (256)**(3-x) * ord(time[x])
                lyrics += "%s%s\r\n" % (ms2timestamp(timems), text)
                content=content[pos+5:]
            return lyrics.encode( "utf-8")
        elif tag.fid == "TXXX":
            if (tag.rawdata[:6] == "Lyrics"):
                return tag.rawdata[7:]
    return None
