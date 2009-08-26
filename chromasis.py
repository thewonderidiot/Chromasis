from Tkinter import *
import tkColorChooser,tkMessageBox,tkSimpleDialog,tkFileDialog,Image,ImageTk,math,paletteOps,copy

class Chromasis:
	def __init__(self, master):
		#Basic stuff
		self.master = master
		master.title("Chromasis")
		master.protocol("WM_DELETE_WINDOW",self.confirmQuit)
		self.changed = False
		ss = self.swatchSize = 32
		xs = self.xswatches = 10
		ys = self.yswatches = 10
		self.defaultFG = (255,255,255)
		self.defaultBG = (0,0,0)
		self.activeOutline = (255,255,255)
		self.inactiveOutline = "self"
		self.dragging = None
		self.palette = {}
		master.resizable(width=False,height=False)
		#master.minsize(width=160, height=80)
		#Build the menu
		menu = Menu(master)
		master.config(menu=menu)
		palettemenu = Menu(menu)
		menu.add_cascade(label="Palette",menu=palettemenu)
		palettemenu.add_command(label="New",command=self.newPalette)
		palettemenu.add_command(label="Settings",command=self.showSettings)
		importmenu = Menu(menu)
		menu.add_cascade(label="Import", menu=importmenu)
		importmenu.add_command(label="From Image",command=self.importImage)
		importmenu.add_command(label="From Python List",command=self.importList)
		importmenu.add_command(label="From File",command=self.importFile)
		exportmenu = Menu(menu)
		menu.add_cascade(label="Export", menu=exportmenu)
		exportmenu.add_command(label="To Image",command=self.exportImage)
		exportmenu.add_command(label="To Python List",command=self.exportList)
		exportmenu.add_command(label="To File",command=self.exportFile)
		
		#Build our canvas
		c = self.colorcanvas = Canvas(master, bg="#000000", height=ss*ys, width=ss*xs, cursor='crosshair')
		c.bind("<ButtonRelease-1>", self.leftClickRelease)
		c.bind("<Button-3>", self.rightClick)
		c.bind("<B1-Motion>",self.drag)
		c.grid(row=0, sticky=W)

	def newPalette(self):
		if self.confirmIfChanges():
			self.palette = {}
			self.colorcanvas.delete(ALL)
			print "Palette erased"
			self.changed = False
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
				if tbo == '':
					return
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
	
	def importFile(self):
		print "Importing palette from a text file."
		colors = []
		done = False
		while not done:
			try:
				tbo = tkFileDialog.askopenfilename(filetypes=[("Text","*.txt")])
				if tbo == '':
					return
				f = open(tbo,"r")
				for c in f.readlines():
					colors.append((int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)))
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
		self.changed = False
	
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
				self.changed = False
				done = True
	
	def exportFile(self):
		print "Exporting current palette to a file."
		done = False
		while not done:
			try:
				tbs = tkFileDialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text File","*.txt")])
				if tbs == None or tbs == '':
					return
				print "Exporting palette file...",
				f = open(tbs,'w')
				for p in self.palette.values():
					f.write("#%02x%02x%02x\n" % p)
				f.close()
			except:
				print "failed."
				if not tkMessageBox.askretrycancel("Export Failed","Error writing image file."):
					return
			else:
				print "done."
				self.changed = False
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
				self.changed = True
				print "Created swatch",r
			else:
				r = a[0]
				newColor = tkColorChooser.askcolor(initialcolor=self.palette[r])
				if newColor[0] == None or newColor[1] == None:
					return
				c.itemconfigure(r,fill=newColor[1],outline=newColor[1])
				self.palette[r] = newColor[0]
				self.changed = True
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
			del self.palette[tbd[0]]
			self.colorcanvas.delete(tbd[0])
			self.changed = True
			print "Deleted swatch",tbd[0]
	
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
			
	def showSettings(self):
		settings = Settings(self)
		
	def updateSettings(self, swatchSize, xswatches, yswatches, defaultFG, defaultBG, activeOutline):
		self.swatchSize = swatchSize
		self.xswatches = xswatches
		self.yswatches = yswatches
		self.defaultFG = defaultFG
		self.defaultBG = defaultBG
		self.activeOutline = activeOutline
		self.colorcanvas.config(bg="#%02x%02x%02x" % defaultBG)
		xsize = max(4+swatchSize*xswatches,160)
		ysize = max(4+swatchSize*yswatches,80)
		self.master.geometry("%dx%d" % (xsize if xsize>160 else 160,4+swatchSize*yswatches))
		self.colorcanvas.config(width=swatchSize*xswatches, height=swatchSize*yswatches)
		print "Settings imported. Redrawing palette with new settings."
		self.colorcanvas.delete(ALL)
		temppalette = self.palette.values()
		self.palette = {}
		self.populatePalette(temppalette)
		
	def notyet(self):
		tkMessageBox.showwarning("Feature Unavailable","This feature has not yet been implemented.")
	
	def confirmIfChanges(self):
		return tkMessageBox.askyesno("Warning!", "Your palette has been changed since that last export. Continue?") if self.changed else True
	
	def confirmQuit(self):
		if self.confirmIfChanges():
			self.master.destroy()

			
class Settings:
	def __init__(self,parent):
		self.parent = parent
		self.w = settings = Toplevel()
		self.defaultBG = parent.defaultBG
		self.defaultFG = parent.defaultFG
		self.activeOutline = parent.activeOutline
		settings.transient(parent.master)
		settings.title("Chromasis - Settings")
		settings.grab_set()
		settings.geometry("+%d+%d" % (parent.master.winfo_rootx()+50,parent.master.winfo_rooty()+50))
		frame = Frame(settings)
		frame.pack(padx=5,pady=5)
		Label(frame,text="Swatch Size:").grid(row=0, sticky=W)
		Label(frame,text="Palette Width:").grid(row=1, sticky=W)
		Label(frame,text="Palette Height:").grid(row=2, sticky=W)
		Label(frame,text="Background Color:").grid(row=3, sticky=W)
		Label(frame,text="Foreground Color:").grid(row=4, sticky=W)
		Label(frame,text="Highlight Color:").grid(row=5, sticky=W)
		#Label(settings,text="Border Color:").grid(row=6, sticky=W)
		self.ss = ss = IntVar()
		ss.set(parent.swatchSize)
		self.xs = xs = IntVar()
		xs.set(parent.xswatches)
		self.ys = ys = IntVar()
		ys.set(parent.yswatches)
		Scale(frame,variable=ss,from_=2,to=256,orient=HORIZONTAL,length=300).grid(row=0,column=1)
		Scale(frame,variable=xs,from_=2,to=256,orient=HORIZONTAL,length=300).grid(row=1,column=1)
		Scale(frame,variable=ys,from_=2,to=256,orient=HORIZONTAL,length=300).grid(row=2,column=1)
		bgb = self.bgButton = Button(frame,width=8,bg="#%02x%02x%02x" % parent.defaultBG,command=self.setBG)
		bgb.grid(row=3,column=1)
		fgb = self.fgButton = Button(frame,width=8,bg="#%02x%02x%02x" % parent.defaultFG,command=self.setFG)
		fgb.grid(row=4,column=1)
		hlb = self.hlButton = Button(frame,width=8,bg="#%02x%02x%02x" % parent.activeOutline,command=self.setHL)
		hlb.grid(row=5,column=1)
		buttons = Frame(settings)
		buttons.pack()
		Button(buttons,text="Okay",width=10,command=self.saveChanges).pack(side=LEFT,padx=5,pady=5)
		Button(buttons,text="Cancel",width=10,command=self.close).pack(side=LEFT,padx=5,pady=5)
		frame.focus_set()
		parent.master.wait_window(settings)


	def setBG(self):
		newColor = tkColorChooser.askcolor(initialcolor=self.bgButton.cget("bg"))
		if newColor[0] == None or newColor[1] == None:
					return
		self.bgButton.config(bg=newColor[1])
		self.defaultBG = newColor[0]
	
	def setFG(self):
		newColor = tkColorChooser.askcolor(initialcolor=self.fgButton.cget("bg"))
		if newColor[0] == None or newColor[1] == None:
					return
		self.fgButton.config(bg=newColor[1])
		self.defaultFG = newColor[0]
		
	def setHL(self):
		newColor = tkColorChooser.askcolor(initialcolor=self.hlButton.cget("bg"))
		if newColor[0] == None or newColor[1] == None:
					return
		self.hlButton.config(bg=newColor[1])
		self.activeOutline = newColor[0]
		
	def saveChanges(self):
		self.parent.updateSettings(swatchSize=self.ss.get(),xswatches=self.xs.get(),yswatches=self.ys.get(),defaultFG=self.defaultFG,defaultBG=self.defaultBG,activeOutline=self.activeOutline)
		self.close()
	
	def close(self):
		self.parent.master.focus_set()
		self.w.destroy()
		
root = Tk()

app = Chromasis(root)

root.mainloop()