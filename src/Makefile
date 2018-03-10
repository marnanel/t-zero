SOURCES = Calendar.inf grammar.h Library.inf \
Things.inf parser.h Present.inf T0english.h T-Zero.inf \
Scoring.inf \
Topiary.inf \
TopiaryRooms.inf \
verblib.h verblibm.h

t-zero.z5: ${SOURCES}
	inform -D +language_name=T0english T-Zero.inf t-zero.z5

TopiaryRooms.inf: make-topiary-rooms-inf.py
	python make-topiary-rooms-inf.py

play: t-zero.z5
	frotz t-zero.z5

test: t-zero.z5
	python t0run.py

