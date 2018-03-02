import json

SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="250"
   height="250"
   viewBox="0 0 210 297"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.1 r15371"
   sodipodi:docname="things.svg">
  <defs
     id="defs2">
    <marker
       inkscape:stockid="Arrow2Mend"
       orient="auto"
       refY="0.0"
       refX="0.0"
       id="Arrow2Mend"
       style="overflow:visible;"
       inkscape:isstock="true">
      <path
         id="path4516"
         style="fill-rule:evenodd;stroke-width:0.625;stroke-linejoin:round;stroke:#000000;stroke-opacity:1;fill:#000000;fill-opacity:1"
         d="M 8.7185878,4.0337352 L -2.2072895,0.016013256 L 8.7185884,-4.0017078 C 6.9730900,-1.6296469 6.9831476,1.6157441 8.7185878,4.0337352 z "
         transform="scale(0.6) rotate(180) translate(0,0)" />
    </marker>
    <marker
       inkscape:stockid="Arrow2Lend"
       orient="auto"
       refY="0.0"
       refX="0.0"
       id="Arrow2Lend"
       style="overflow:visible;"
       inkscape:isstock="true">
      <path
         id="path4510"
         style="fill-rule:evenodd;stroke-width:0.625;stroke-linejoin:round;stroke:#000000;stroke-opacity:1;fill:#000000;fill-opacity:1"
         d="M 8.7185878,4.0337352 L -2.2072895,0.016013256 L 8.7185884,-4.0017078 C 6.9730900,-1.6296469 6.9831476,1.6157441 8.7185878,4.0337352 z "
         transform="scale(1.1) rotate(180) translate(1,0)" />
    </marker>
  </defs>
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="0.49497475"
     inkscape:cx="-6.4279526"
     inkscape:cy="931.91121"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     inkscape:window-width="1366"
     inkscape:window-height="704"
     inkscape:window-x="0"
     inkscape:window-y="27"
     inkscape:window-maximized="1" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
	%(arrows)s
	%(rooms)s
</svg>"""


ROOM_TEMPLATE = """
    <circle
       style="opacity:1;fill:none;fill-opacity:1;stroke:#0ffa0f;stroke-width:2.64583325;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:0.66666667"
       id="%(id)s"
       cx="%(x)f"
       cy="%(y)f"
       r="%(radius)f" />
"""

EXIT_TEMPLATE = """
    <circle
       style="opacity:1;fill:%(colour)s;fill-opacity:1;stroke:none;stroke-width:2.64583325;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0"
       id="%(id)s"
       cx="%(x)f"
       cy="%(y)f"
       r="%(radius)f" />
"""


ARROW_TEMPLATE = """
    <path
       style="fill:none;fill-rule:evenodd;stroke:#aaaaff;stroke-width:2;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:0.5;stroke-miterlimit:4;stroke-dasharray:none;"
       d="M %(x1)f,%(y1)f L %(x2)f,%(y2)f"
       id="%(id)s"
       inkscape:connector-curvature="0"
       sodipodi:nodetypes="cc" />
"""

def delta_from_direction(d):
	if d=='n':
		return 0, -1
	elif d=='e':
		return 1,0
	elif d=='s':
		return 0,1
	elif d=='w':
		return -1, 0
	elif d=='x':
		return 0, 0
	else:
		raise ValueError("unknown direction: "+d)

def room_position_from_id(room, direction=None, arrow=False):
	x = (int(room[1])) * 50
	y = (int(room[2])) * 50

	dx, dy = delta_from_direction(room[3])

	x -= dx*10
	y -= dy*10

	if direction is not None:
		dx, dy = delta_from_direction(direction)
		
		if arrow:
			x -= dx*10
			y -= dy*10
		else:
			x += dx*4
			y += dy*4

	return x,y

def main():
	topiary = json.load(open('topiary.json', 'r'))

	rooms = set(['c'+x[0:5].replace('-','') for x in topiary.keys()])

	svg_vars = {
		'rooms': '',
		'arrows': '',
	}

	for x in range(5):
		for y in range(5):
			
			ersatz_id = 'c%d%dx' % (x, y+1)
			nx, ny = room_position_from_id(ersatz_id)

			room_vars = {
				'id': ersatz_id,
				'x': nx,
				'y': ny,
				'radius': 15,
			}

			svg_vars['rooms'] += ROOM_TEMPLATE % room_vars

	for room in rooms:

		x, y = room_position_from_id(room)

		room_vars = {
			'id': room,
			'x': x,
			'y': y,
			'radius': 6,
		}

		svg_vars['rooms'] += ROOM_TEMPLATE % room_vars

		for d in ('n', 'e', 's', 'w'):

			move_name = '%s-%s-%s.sav %s' % (
				room[1],
				room[2],
				room[3],
				d)

			if move_name not in topiary:
				continue

			x, y = room_position_from_id(room, d)

			exit_vars = {
				'x': x,
				'y': y,
				'radius': 2,
				'id': room+d,
			}

			if topiary[move_name]=='move':

				exit_vars['colour'] = '#0077ff'

				new_room_x = int(room[1])
				new_room_y = int(room[2])

				if d=='n':
					new_room_y -= 1
				elif d=='e':
					new_room_x += 1
				elif d=='s':
					new_room_y += 1
				elif d=='w':
					new_room_x -= 1

				target_room = 'c%d%d%s' % (new_room_x, new_room_y, d)

				x2, y2 = room_position_from_id(target_room,
					arrow=True)

				arrow_vars = {
					'x1': x,
					'y1': y,
					'x2': x2,	
					'y2': y2,
					'id': room+target_room,
				}

				svg_vars['arrows'] += ARROW_TEMPLATE % arrow_vars

			elif topiary[move_name]=='hedge':
				exit_vars['colour'] = '#007700'
			elif topiary[move_name]=='uturn':
				exit_vars['colour'] = '#aaaaaa'
			elif topiary[move_name]=='block':
				exit_vars['colour'] = '#770000'
			else:
				exit_vars['colour'] = '#000000'

			svg_vars['rooms'] += EXIT_TEMPLATE % exit_vars

	open('topiary-map.svg', 'w').write(SVG_TEMPLATE % svg_vars)

if __name__=='__main__':
	main()
