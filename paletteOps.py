import Image,ImageDraw,math

def distance((x1,y1,z1),(x2,y2,z2)):
	return math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)

def findClosest(color, palette):
	mindist = 99999
	closest = (255,255,255)
	for p in palette:
		dist = distance(color,p)
		if dist < mindist:
			mindist = dist
			closest = p
	return closest

def reduce(infile, palette):
	img = Image.open(img)
	sx,sy = img.size
	out = Image.new("RGB",(sx,sy),"#ffffff")
	d = out.load()
	s = img.load()
	for y in range(0,sy-1):
		for x in range(0,sx-1):
			d[x,y] = findClosest(s[x,y],palette)
	return d

def index(infile,palette):
	print "Indexing",infile
	img = Image.open(infile)
	sx,sy = img.size
	colors = img.getcolors(sx*sy)
	majors = {}
	print "Generating color dictionary...",
	for p in palette:
		majors["#%02x%02x%02x" % p] = 0;
	print "done.\nIndexing major colors...",
	for c in colors:
		n = findClosest(c[1][:3],palette)
		key = "#%02x%02x%02x" % n
		majors[key] = majors[key] + c[0]
	print "done.\nDropping nonpresent colors and sorting...",
	zeroes = []
	for c in majors:
		if majors[c] == 0:
			zeroes.append(c)
	for z in zeroes:
		del majors[z]
	print "done."
	majors = sorted(majors.items(), key=lambda(color,num):(num,color), reverse=1)

	return majors
	