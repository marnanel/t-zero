import Tzero

test = Tzero.Tzero()
print 'Created: ', test

test.save('initial')
print test.move('ne')
test.converse('undo')
print test.move('nw')
test.close()

