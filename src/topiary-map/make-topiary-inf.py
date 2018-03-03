import json

DIRECTIONS = ('n', 'e', 's', 'w')

def main():
    topiary = json.load(open('topiary.json', 'r'))

    print '! Generated file. Do not edit.'
    print '! Made by make-topiary-rooms-inf.py.'
    print

    for y in range(5):
        for x in range(5):

            traffic_rules = 0

            for entering in DIRECTIONS:
                for leaving in DIRECTIONS:

                    traffic_rules <<= 1

                    # y was accidentally set to 1-based
                    key = '%d-%d-%s.sav %s' % (x, y+1, entering, leaving)

                    if topiary.get(key, '') in ('uturn', 'block'):
                        traffic_rules |= 1

            print 'TopiaryRoom "Topiary" Topiary%d%d' % (x, y)
            print 'with'

            for direction in DIRECTIONS:

                new_x = x
                new_y = y

                if direction=='n':
                    new_y -= 1
                elif direction=='e':
                    new_x += 1
                elif direction=='s':
                    new_y += 1
                elif direction=='w':
                    new_x -= 1
                else:
                    raise ValueError(direction)

                print '%s_to' % (direction,)
                print '    ',

                if (x, y, direction) == (0,1,'w'):
                    print 'TopiaryEntrance,'
                elif (x, y, direction) == (4,3,'e'):
                    print 'AmazingSpace,' # win
                elif (x, y, direction) in [(2,3,'e'), (3,3,'w')]:
                    print 'TOPIARY_MIDDLE_HEDGE,'
                elif new_x<0 or new_y<0 or new_x>4 or new_y>4:
                    print 'TOPIARY_EDGE_HEDGE,'
                else:
                    print 'Topiary%d%d,' % (new_x, new_y)

            print 'traffic_rules'
            print '   $%x;' % (traffic_rules,)
            print

if __name__=='__main__':
    main()
