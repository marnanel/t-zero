import json
import re

def chimes_transform(data):

    result = {}

    for room, message in data.items():

        if room.endswith('.'):
            room = room[:-1]

        result[room] = 0

        for value, keyword in [(1, 'nearby'), (2, 'faraway')]:
            if keyword in message:
                result[room] = value

    return result


def scan_source(sourcecode, data):

    print data

    source = open(sourcecode, 'r')

    for line in source.readlines():
        m = re.match(r'^Object.*"(.*)"', line)
        if m:
            roomname = m.groups()[0]
            if roomname.endswith('.'):
                roomname = roomname[:-1]

            print roomname, roomname in data

def main(source, transformation, sourcecode):
    data = json.load(open(source, 'r'))
    data = transformation(data)

    scan_source(
            sourcecode = sourcecode,
            data = data,
            )

if __name__=='__main__':
    main(
        source='chimes-where',
        transformation=chimes_transform,
        sourcecode='Present.inf',
        )
