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
	img = img.convert("RGB")
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
	majors = sorted(majors.items(), key=lambda(color,num):(num,color), reverse=True)

	return majors
	
def getColors(infile):
	print "Opening image",infile
	img = Image.open(infile)
	print "Converting to RGB..."
	img = img.convert("RGB")
	sx, sy = img.size
	print "Grabbing colors..."
	colors = img.getcolors(sx*sy)
	print "Sorting..."
	return [p[1] for p in sorted(colors,reverse=True)]
	
def drawPalette(outfile, palette, swatchSize, xswatches, yswatches):
	img = Image.new("RGB",(swatchSize*xswatches,swatchSize*yswatches),"#000000")
	d = ImageDraw.Draw(img)
	x=y=0
	for p in palette:
		d.rectangle([(x,y),(x+swatchSize-1,y+swatchSize-1)],fill="#%02x%02x%02x" % p)
		x = x+swatchSize
		if x >= swatchSize * xswatches:
			x = 0
			y = y+swatchSize
	del d
	img.save(outfile)