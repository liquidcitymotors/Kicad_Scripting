import pcbnew
import xml.etree.ElementTree

def slug_to_identifier(slug):
	if len(slug) == 0 or slug[0].isdigit():
		slug = "_" + slug
	slug = slug[0].upper() + slug[1:]
	slug = slug.replace('-', '_')
	return slug

def read_guide(panel_filename=None, board_filename=None):
	print(panel_filename)

	# Read SVG XML
	tree = xml.etree.ElementTree.parse(panel_filename)

	return panel_to_components(tree)

def panel_to_components(tree):
	ns = {
		"svg": "http://www.w3.org/2000/svg",
		"inkscape": "http://www.inkscape.org/namespaces/inkscape",
	}

	# Get components layer
	root = tree.getroot()
	groups = root.findall(".//svg:g[@inkscape:label='Drill']", ns)

	# Get circles and rects
	components_group = groups[0]
	circles = components_group.findall(".//svg:circle", ns)
	ellipses = components_group.findall(".//svg:ellipse", ns)

	groups = root.findall(".//svg:g[@inkscape:label='pcb']", ns)
	# Get circles and rects
	components_group = groups[0]
	pcb = components_group.findall(".//svg:rect", ns)[0]

	print(pcb)
	#
	print(pcb.get('x'))
	x_offset = -float(pcb.get('x'))
	print(pcb.get('y'))
	y_offset = -float(pcb.get('y'))

	components = {}

	for el in circles + ellipses:
		c = {}
		# Get name
		name = el.get('{http://www.inkscape.org/namespaces/inkscape}label')
		if name is None:
			name = el.get('id')
		name = slug_to_identifier(name).upper()

		cx = float(el.get('cx')) + x_offset
		cy = float(el.get('cy')) + y_offset

		components[name] = {}
		components[name]['x'] = round(cx, 4)
		components[name]['y'] = round(cy, 4)

	return components


guide = read_guide('/Users/willmitchell/Documents/CPSOS_Modulation_PCB/CPSOS_Modulation_Guide.svg')

board = pcbnew.LoadBoard("/Users/willmitchell/Documents/CPSOS_Modulation_PCB/CPSOS_Modulation_PCB.kicad_pcb")

layertable = {}
numlayers = pcbnew.PCB_LAYER_ID_COUNT
for i in range(numlayers):
	layertable[board.GetLayerName(i)] = i

print(board.GetBoardEdgesBoundingBox().GetWidth())

matches = []

for module in board.GetModules():
	value = module.GetValue()
	if value in guide:
		matches.append(module.GetValue())
		x = int(guide[value]["x"] * 1000000 + 20000000)
		y = int(guide[value]["y"] * 1000000 + 20000000)
		p = module.GetPosition()
		if (p.x != x) or (p.y != y):
			print "* Module: %s" % module.GetValue()
			print "* x: %s" % p.x
			print "* y: %s" % p.y
			p.x = x
			p.y = y
			module.SetPosition(p)

board.Save("/Users/willmitchell/Documents/CPSOS_Modulation_PCB/CPSOS_Modulation_PCB.kicad_pcb")

