from Tkinter import *
import tkColorChooser,tkMessageBox,tkSimpleDialog,tkFileDialog,Image,ImageTk,math,paletteOps

class Chromasis:
	def __init__(self, master):
		#Basic stuff
		self.master = master
		master.title("Chromasis")
		ss = self.swatchSize = 32
		xs = self.xswatches = 10
		ys = self.yswatches = 10
		self.defaultFG = (255,255,255)
		self.activeOutline = (255,255,255)
		self.inactiveOutline = "self"
		self.dragging = None
		self.palette = {}
		master.minsize(width=4+ss*xs, height=4+ss*ys)
		#Build the menu
		menu = Menu(master)
		master.config(menu=menu)
		palettemenu = Menu(menu)
		menu.add_cascade(label="Palette",menu=palettemenu)
		palettemenu.add_command(label="New",command=self.newPalette)
		palettemenu.add_command(label="Settings",command=self.notyet)
		importmenu = Menu(menu)
		menu.add_cascade(label="Import", menu=importmenu)
		importmenu.add_command(label="From Image",command=self.importImage)
		importmenu.add_command(label="From Python List",command=self.importList)
		importmenu.add_command(label="From File",command=self.notyet)
		exportmenu = Menu(menu)
		menu.add_cascade(label="Export", menu=exportmenu)
		exportmenu.add_command(label="To Image",command=self.exportImage)
		exportmenu.add_command(label="To Python List",command=self.exportList)
		exportmenu.add_command(label="To File",command=self.notyet)
		
		#Build our canvas
		c = self.colorcanvas = Canvas(master, bg="#000000", height=ss*ys, width=ss*xs, cursor='crosshair')
		c.bind("<ButtonRelease-1>", self.leftClickRelease)
		c.bind("<Button-3>", self.rightClick)
		c.bind("<B1-Motion>",self.drag)
		c.grid(row=0, sticky=W)

	def newPalette(self):
		if tkMessageBox.askyesno("Warning!", "This will erase your current palette. Continue?"):
			self.palette = {}
			self.colorcanvas.delete(ALL)
			print "Palette erased"
			return True
		return False
	
	def importList(self):
		print "Importing palette from a Python list."
		done = False
		newlist = []
		while not done:
			try:
				newlist = tkSimpleDialog.askstring("Import Python List","Enter a Python list of (R,G,B) tuples.")
				if newlist == None:
					return
				newlist = eval(newlist)
				print "Checking if input is a list...",
				if type(newlist) != type([]):
					raise IOError("Invalid list")
				print "okay.\nChecking contents of list...",
				for l in newlist:
					if type(l) != type(()) or len(l) != 3 or (not l[0] in range(0,256)) or (not l[1] in range(0,256)) or (not l[2] in range(0,256)):
						raise IOError("Invalid list")
				print "okay."
			except:
				print "failed."
				if not tkMessageBox.askretrycancel("Import Failed","Invalid python list was entered."):
					return
			else:
				if not self.newPalette():
					return
				self.populatePalette(newlist)
				done = True
				print "Import complete."

	def importImage(self):
		colors = []
		done = False
		while not done:
			try:
				tbo = tkFileDialog.askopenfilename(filetypes=[("Images","*.png"),("Images","*.jpg"),("Images","*.gif")])
				colors = paletteOps.getColors(tbo)
			except:
				print "Failed."
				if not tkMessageBox.askretrycancel("Import Failed","Error reading image file."):
					return
			else:
				if not self.newPalette():
					return
				self.populatePalette(colors)
				done = True
				print "Import complete."
	
	def populatePalette(self,newpalette):
		c = self.colorcanvas
		ss = self.swatchSize
		xs = self.xswatches
		ys = self.yswatches
		x=y=2
		for l in newpalette:
			print "Importing",l
			if self.inactiveOutline == "self":
				outline = "#%02x%02x%02x" % l
			else:
				outline = "#%02x%02x%02x" % self.inactiveOutline
			r = c.create_rectangle(x,y,x+ss-1,y+ss-1,  fill="#%02x%02x%02x" % l,outline=outline,activeoutline="#%02x%02x%02x" % self.activeOutline)
			self.palette[r] = l
			x = x + ss
			if (x >= ss*xs):
				x = 2
				y = y + ss
			if (y >= ss*ys):
				print "Size of window exceeded. Not all colors could be imported."
				break
	
	def exportList(self):
		print "Exporting current palette to python list."
		self.master.clipboard_append(str(self.palette.values()))
		tkMessageBox.showinfo("Palette Exported", "A python list representing the palette has been copied to your clipboard.")
	
	def exportImage(self):
		print "Exporting current palette to an image."
		done = False
		while not done:
			try:
				tbs = tkFileDialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")])
				if tbs == None or tbs == '':
					return
				print "Exporting palette image...",
				paletteOps.drawPalette(tbs,self.palette.values(),self.swatchSize,self.xswatches,self.yswatches)
			except:
				print "failed."
				if not tkMessageBox.askretrycancel("Export Failed","Error writing image file."):
					return
			else:
				print "done."
				done = True
	
	def leftClickRelease(self, event):
		c = self.colorcanvas
		ss = self.swatchSize
		xs = self.xswatches
		ys = self.yswatches
		if self.dragging == None or self.dragging == "empty":
			self.dragging = None
			x,y = c.canvasx(event.x),c.canvasy(event.y)
			x,y = 2+ss*math.floor(x/ss), 2+ss*math.floor(y/ss)
			a = c.find_overlapping(x+ss/2,y+ss/2,x+ss/2,y+ss/2)
			if len(a)==0:
				if x > ss*xs or x < 0 or y > ss*ys or y < 0:
					return
				if self.inactiveOutline == "self":
					outline = "#%02x%02x%02x" % self.defaultFG
				else:
					outline = "#%02x%02x%02x" % self.inactiveOutline
				r = c.create_rectangle(x,y,x+ss-1,y+ss-1, fill="#%02x%02x%02x" % self.defaultFG,outline=outline,activeoutline="#%02x%02x%02x" % self.activeOutline)
				self.palette[r] = self.defaultFG
				print "Created swatch",r
			else:
				r = a[0]
				newColor = tkColorChooser.askcolor(initialcolor=self.palette[r])
				if newColor[0] == None or newColor[1] == None:
					return
				c.itemconfigure(r,fill=newColor[1],outline=newColor[1])
				self.palette[r] = newColor[0]
				print "Filled swatch",r,"with",newColor[1]
		else:
			rpos = c.coords(self.dragging)
			x,y = rpos[0]+ss/2,rpos[1]+ss/2
			occupied = c.find_overlapping(x,y,x,y)
			if len(occupied) > 1:
				swap = occupied[1] if self.dragging == occupied[0] else occupied[0]
				print "Swapping swatches",self.dragging,"and",swap
				c.coords(swap,self.dox,self.doy,self.dox+ss-1,self.doy+ss-1)
			x,y = 2+ss*math.floor(x/ss), 2+ss*math.floor(y/ss)
			if x < 0:
				x = 0
			if x > ss*xs:
				x = 2+ss*(xs-1)
			if y < 0:
				y = 0
			if y > ss*ys:
				y = 2+ss*(ys-1)
			c.coords(self.dragging,x,y,x+ss-1,y+ss-1)
			print "Swatch",self.dragging,"dropped"
			self.dragging = None
		
	def rightClick(self, event):
		x,y = self.colorcanvas.canvasx(event.x),self.colorcanvas.canvasy(event.y)
		tbd = self.colorcanvas.find_overlapping(x,y,x,y)
		if len(tbd)!=0:
			print "Deleted swatch",tbd[0]
			del self.palette[tbd[0]]
			self.colorcanvas.delete(tbd[0])
	
	def drag(self, event):
		c = self.colorcanvas
		x,y = c.canvasx(event.x),c.canvasy(event.y)
		if self.dragging == None:
			a = c.find_overlapping(x,y,x,y)
			if len(a)!=0:
				self.dragging = a[0]
				c.lift(self.dragging)
				rpos = c.coords(self.dragging)
				self.dox = rpos[0]
				self.doy = rpos[1]
				self.dxoffset = x - rpos[0]
				self.dyoffset = y - rpos[1]
				print "Dragging swatch",self.dragging
			else:
				self.dragging = "empty"
		elif self.dragging != "empty":
			x = x-self.dxoffset
			y = y-self.dyoffset
			c.coords(self.dragging,x,y,x+self.swatchSize-1,y+self.swatchSize-1)
		
	def notyet(self):
		tkMessageBox.showwarning("Feature Unavailable","This feature has not yet been implemented.")
root = Tk()

app = Chromasis(root)

root.mainloop()