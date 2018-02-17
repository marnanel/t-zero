import json

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

def main(source, transformation):
    data = json.load(open(source, 'r'))

    data = transformation(data)

    print data

if __name__=='__main__':
    main(
        source='chimes-where',
        transformation=chimes_transform,
        )
