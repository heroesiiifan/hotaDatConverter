#!/usr/bin/env python3

#compile to exe with: pyinstaller --noconsole --onefile hotaDatConverter.py

import struct
import json
import argparse

def extractDat(filename, encoding="cp1252"):
    fh = open(filename, "rb")

    data = []

    assert struct.unpack("4s", fh.read(4))[0] == b'HDAT'
    assert struct.unpack("i", fh.read(4))[0] == 2

    count = struct.unpack("i", fh.read(4))[0]

    for _ in range(count):
        tmp = {}
        strlen = struct.unpack("i", fh.read(4))[0]
        tmp["name"] = struct.unpack(str(strlen) + "s", fh.read(strlen))[0].decode(encoding)
        strlen = struct.unpack("i", fh.read(4))[0]
        tmp["foldername"] = struct.unpack(str(strlen) + "s", fh.read(strlen))[0].decode(encoding)
        assert struct.unpack("i", fh.read(4))[0] == 9
        tmp["data"] = {}
        for i in range(9):
            strlen = struct.unpack("i", fh.read(4))[0]
            tmp["data"][i] = struct.unpack(str(strlen) + "s", fh.read(strlen))[0].decode(encoding)
        if struct.unpack("?", fh.read(1))[0] == True:
            strlen = struct.unpack("i", fh.read(4))[0]
            tmp["data"][9] = ''.join(struct.pack("B", x).hex() for x in struct.unpack(str(strlen) + "s", fh.read(strlen))[0])
        strlen = struct.unpack("i", fh.read(4))[0]
        tmp["data"][10] = [struct.unpack("i", fh.read(4))[0] for _ in range(strlen)]
    
        data.append(tmp)

    return data

def createDat(filename, data, encoding="cp1252"):
    fh = open(filename, "wb")

    fh.write(struct.pack("4s", b'HDAT'))
    fh.write(struct.pack("i", 2))
    fh.write(struct.pack("i", len(data)))

    for i in range(len(data)):
        fh.write(struct.pack("i", len(data[i]["name"])))
        fh.write(struct.pack(str(len(data[i]["name"])) + "s", str(data[i]["name"]).encode(encoding)))
        fh.write(struct.pack("i", len(data[i]["foldername"])))
        fh.write(struct.pack(str(len(data[i]["foldername"])) + "s", str(data[i]["foldername"]).encode(encoding)))
        fh.write(struct.pack("i", 9))
        for j in range(9):
            fh.write(struct.pack("i", len(data[i]["data"][str(j)])))
            fh.write(struct.pack(str(len(data[i]["data"][str(j)])) + "s", str(data[i]["data"][str(j)]).encode(encoding)))
        fh.write(struct.pack("?", "9" in data[i]["data"]))
        if "9" in data[i]["data"]:
            tmp = bytes.fromhex(data[i]["data"]["9"])
            fh.write(struct.pack("i", len(tmp)))
            fh.write(struct.pack(str(len(tmp)) + "s", tmp))
        fh.write(struct.pack("i", len(data[i]["data"]["10"])))
        for j in range(len(data[i]["data"]["10"])):
            fh.write(struct.pack("i", data[i]["data"]["10"][j]))

parser = argparse.ArgumentParser(
                    prog='HotA dat converter',
                    description='convert HotA dat to json and vice versa')
parser.add_argument('filename')
parser.add_argument('-e', '--encoding', help="python text encoding")

args = parser.parse_args()

filename = str(args.filename)
encoding = str(args.encoding) if args.encoding != None else "cp1252"

if filename.lower().endswith(".json"):
    createDat(filename.rsplit('.', 1)[0] + ".dat", json.loads(open(filename, encoding=encoding).read()), encoding=encoding)
if filename.lower().endswith(".dat"):
    open(filename.rsplit('.', 1)[0] + ".json", "wb").write(json.dumps(extractDat(filename, encoding=encoding), ensure_ascii=False, indent=2).encode(encoding))