import json

DIRECTIONS = ('n', 'e', 's', 'w')

def main():

    print 'Creating topiary map...',

    topiary = json.load(open('topiary.json', 'r'))
    output = open('TopiaryRooms.inf', 'w')

    output.write('! Generated file. Do not edit.\n')
    output.write('! Made by make-topiary-rooms-inf.py.\n')
    output.write('\n')

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

            output.write('TopiaryRoom Topiary%d%d "Topiary of Time"\n' % (x, y))
            output.write('with\n')
            output.write('pos_x\n')
            output.write('   %d,\n' % (x,))
            output.write('pos_y\n')
            output.write('   %d,\n' % (y,))

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

                output.write('%s_to\n' % (direction,))
                output.write('    ')

                if (x, y, direction) == (0,1,'w'):
                    output.write('TopiaryEntrance,\n')
                elif (x, y, direction) == (4,3,'e'):
                    output.write('AmazingSpace,\n') # win
                elif (x, y, direction) in [(2,3,'e'), (3,3,'w')]:
                    output.write('TOPIARY_MIDDLE_HEDGE,\n')
                elif new_x<0 or new_y<0 or new_x>4 or new_y>4:
                    output.write('TOPIARY_EDGE_HEDGE,\n')
                else:
                    output.write('Topiary%d%d,\n' % (new_x, new_y))

            output.write('traffic_rules\n')
            output.write('   $%x;\n' % (traffic_rules,))
            output.write('\n')

    output.close()

    print 'done.'

if __name__=='__main__':
    main()
