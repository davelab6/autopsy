#FLM: Autopsy 1.1
# -*- coding: cp1252 -*-



########################################################################
#
#   Autopsy Visual Font Auditing
#   1.1
#
#   (c) 2009 by Yanone
#
#   http://www.yanone.de/typedesign/autopsy/
#
#   GPLv3 or later
#
########################################################################



from FL import *
import time, os, string, math, random
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
mm = cm / 10


##### Misc.

class Ddict(dict):
    def __init__(self, default=None):
        self.default = default
       
    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)


##### Settings

programname = 'Autopsy'
programversion = '1.101'
releasedate = '201302101234'
verbose = False

availablegraphs = ('width', 'bboxwidth', 'bboxheight', 'highestpoint', 'lowestpoint', 'leftsidebearing', 'rightsidebearing')

graphrealnames = {
	'width' : 'Width',
	'bboxwidth' : 'BBox Width',
	'bboxheight' : 'BBox Height',
	'highestpoint' : 'BBox Highest',
	'lowestpoint' : 'BBox Lowest',
	'leftsidebearing' : 'L Sidebearing',
	'rightsidebearing' : 'R Sidebearing',
	}


pagemargin = Ddict(dict)
pagemargin['left'] = 8
pagemargin['right'] = 8
pagemargin['top'] = 8
pagemargin['bottom'] = 11
scrapboard = Ddict(dict)
graphcoords = Ddict(dict)

# separator between the scrapboard and the tablesboard
headmargin = 15 # mm
separator = 8 # mm
tableseparator = 3 # mm
roundedcorners = 3 # (pt?)
guidelinedashed = (3, 3) # pt on, pt off

# Colors
colourguides = (1, .5, 0, 0)
colourglobalguides = (0, 1, 1, 0)

# Headline
headerheight = 8 # mm
headlinefontsize = 14
#pdfcolour = (0, .05, 1, 0)
pdfcolour = (.25, 0, 1, 0)
#headlinefontcolour = (.25, .25, 1, .8)
headlinefontcolour = (0, 0, 0, 1)


pdffont = Ddict(dict)
pdffont['Regular'] = 'Courier'
pdffont['Bold'] = 'Courier-Bold'


graphcolour = Ddict(dict)
graphcolour['__default__'] = pdfcolour
graphcolour['width'] = (0, .9, .9, 0)
graphcolour['bboxwidth'] = (0, .75, .9, 0)
graphcolour['bboxheight'] = (0, .5, 1, 0)
graphcolour['highestpoint'] = (0, .3, 1, 0)
graphcolour['lowestpoint'] = (0, .1, 1, 0)
graphcolour['leftsidebearing'] = (0, .75, .25, 0)
graphcolour['rightsidebearing'] = (.25, .75, .25, 0)

# Metrics
glyphcolour = (0, 0, 0, 1)
xrayfillcolour = (0, 0, 0, .4)
metricscolour = (0, 0, 0, .5)
metricslinewidth = .5 # pt
scrapboardcolour = (0, 0, 0, 1)
drawboards = False


# Graphs
#tablenamefont = pdffont['Regular']
graphnamefontsize = 8
#pointsvaluefont = pdffont['Regular']
pointsvaluefontsize = 8


############ Classes


class Report:
	def __init__(self):
		self.gridcolour = metricscolour
		self.strokecolour = pdfcolour
		self.gridwidth = metricslinewidth
		self.strokewidth = 1
		self.values = [] # (value, glyphwidth, glyphheight)
		self.pointslist = []
#		self.scope = 'local' # local or global (relative to this single glyph, or to all glyphs in the pdf)
		self.glyphname = ''
		self.graphname = ''
		
		self.min = 0
		self.max = 0
		self.sum = 0
		ratio = 0

	def addvalue(self, value):
		self.values.append(value)
		
		if len(self.values) == 1:
			self.min = value[0]
			self.max = value[0]
		
		if value[0] > self.max:
			self.max = value[0]
		if value[0] < self.min:
			self.min = value[0]
		self.sum += value[0]

	def draw(self):
		global myDialog
		global globalscopemin, globalscopemax
		global glyphs
		
		drawrect(self.left * mm, self.bottom * mm, self.right * mm, self.top * mm, '', self.gridcolour, self.gridwidth, None, roundedcorners)


		r = .05
		mymin = self.min - int(math.fabs(self.min) * r)
		mymax = self.max + int(math.fabs(self.max) * r)


		if self.scope == 'global':
			
			# Walk through the other graphs and collect their min and max values
			for glyph in glyphs:
				
				try:
					if reports[glyph][self.graphname].min < mymin:
						mymin = reports[glyph][self.graphname].min
				except:
					mymin = reports[glyph][self.graphname].min
				
				try:
					if reports[glyph][self.graphname].max > mymax:
						mymax = reports[glyph][self.graphname].max
				except:
					mymax = reports[glyph][self.graphname].max
				
		if mymax - mymin < 10:
			mymin -= 5
			mymax += 5

		pointslist = []

		
		if myDialog.orientation == 'portrait':
			if myDialog.drawpointsvalues == 1:
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.left * mm + 1*mm, self.bottom * mm - 3*mm, int(mymin))
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm - 5*mm, self.bottom * mm - 3*mm, int(mymax))
			
			try:
				localratio = (self.right - self.left) / (mymax - mymin)
			except:
				localratio = 0

			try:
				y = self.top - (self.values[0][2] / 2 / mm * ratio)
			except:
				y = self.top

			for i, value in enumerate(self.values):
				x = self.left + (value[0] - mymin) * localratio
				pointslist.append((value[0], x, y))
				try:
					y -= self.values[i+1][2] / mm * ratio
				except:
					pass
			


		else:
			if myDialog.drawpointsvalues == 1:
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm + 1*mm, self.bottom * mm + 1*mm, int(mymin))
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm + 1*mm, self.top * mm - 3*mm, int(mymax))
#			DrawText(pdffont['Regular'], graphnamefontsize, self.gridcolour, self.left * mm + 1.7*mm, self.top * mm - 4*mm, graphrealnames[self.graphname])

			try:
				localratio = (self.top - self.bottom) / (mymax - mymin)
			except:
				localratio = 0

			try:
				position = self.left + (self.values[0][1] / 2 / mm * ratio)
			except:
				position = self.left

			for i, value in enumerate(self.values):
				x = position
				y = self.bottom + (value[0] - mymin) * localratio
				pointslist.append((value[0], x, y))
				try:
					position += self.values[i+1][1] / mm * ratio
				except:
					pass


		# Calculate thickness of stroke according to scope of graph
		minthickness = 2
		maxthickness = 8
		thickness = -.008 * (mymax - mymin) + maxthickness
		if thickness < minthickness:
			thickness = minthickness
		elif thickness > maxthickness:
			thickness = maxthickness
		
		DrawTableLines(pointslist, self.strokecolour, thickness)
		DrawText(pdffont['Regular'], graphnamefontsize, self.gridcolour, self.left * mm + 1.7*mm, self.top * mm - 4*mm, graphrealnames[self.graphname])

class PDFPath:
	def __init__(self):
		self.pathobject = pdf.beginPath()
		self.fill = 1
		self.fillcolour = (0,0,0,1)
		self.stroke = 0
		self.strokecolour = (0,0,0,1)
		self.strokewidth = 1
#
#
#		self.pathobject = pdf.beginPath()
#		self.stroke = stroke
#		self.fill = fill
#		self.strokecolour = strokecolour
#		self.fillcolour = fillcolour
#		self.strokewidth = strokewidth
		pdf.setStrokeColorCMYK(self.strokecolour[0], self.strokecolour[1], self.strokecolour[2], self.strokecolour[3])
		pdf.setFillColorCMYK(self.fillcolour[0], self.fillcolour[1], self.fillcolour[2], self.fillcolour[3])
		pdf.setLineWidth(self.strokewidth)
		self.dashed = (1)

	def moveTo(self, x, y):
		self.pathobject.moveTo(x, y)

	def lineTo(self, x, y):

		pdf.setLineWidth(self.strokewidth)
		pdf.setStrokeColorCMYK(self.strokecolour[0], self.strokecolour[1], self.strokecolour[2], self.strokecolour[3])
		pdf.setFillColorCMYK(self.fillcolour[0], self.fillcolour[1], self.fillcolour[2], self.fillcolour[3])

		self.pathobject.lineTo(x, y)
		
	def curveTo(self, coords):
		pdf.setLineWidth(self.strokewidth)
		pdf.setStrokeColorCMYK(self.strokecolour[0], self.strokecolour[1], self.strokecolour[2], self.strokecolour[3])
		pdf.setFillColorCMYK(self.fillcolour[0], self.fillcolour[1], self.fillcolour[2], self.fillcolour[3])
		self.pathobject.curveTo(coords[1][0], coords[1][1], coords[2][0], coords[2][1], coords[0][0], coords[0][1])

	def close(self):
		pdf.setLineWidth(self.strokewidth)
		pdf.setStrokeColorCMYK(self.strokecolour[0], self.strokecolour[1], self.strokecolour[2], self.strokecolour[3])
		pdf.setFillColorCMYK(self.fillcolour[0], self.fillcolour[1], self.fillcolour[2], self.fillcolour[3])
		self.pathobject.close()

	def draw(self):
		pdf.setLineWidth(self.strokewidth)
		pdf.setStrokeColorCMYK(self.strokecolour[0], self.strokecolour[1], self.strokecolour[2], self.strokecolour[3])
		pdf.setFillColorCMYK(self.fillcolour[0], self.fillcolour[1], self.fillcolour[2], self.fillcolour[3])
		pdf.setDash(self.dashed)
		pdf.drawPath(self.pathobject, stroke = self.stroke, fill = self.fill)

		
		
#################################

def SetScrapBoard(pageratio):
	global myDialog
	
	scrapboard['left'] = pagemargin['left']
	scrapboard['right'] = pagewidth/mm - pagemargin['right']
	scrapboard['top'] = pageheight/mm - pagemargin['top'] - headmargin
	scrapboard['bottom'] = pagemargin['bottom']
	graphcoords['left'] = pagemargin['left']
	graphcoords['right'] = pagewidth/mm - pagemargin['right']
	graphcoords['top'] = pageheight/mm - pagemargin['top'] - headmargin
	graphcoords['bottom'] = pagemargin['bottom']

	# Recalculate drawing boards
	if myDialog.orientation == 'portrait':
		availablewidth = pagewidth/mm - pagemargin['left'] - pagemargin['right']
		partial = availablewidth * pageratio
		scrapboard['right'] = pagemargin['left'] + partial - separator / 2
		graphcoords['left'] = scrapboard['right'] + separator
	else:
		availablewidth = pageheight/mm - pagemargin['top'] - pagemargin['bottom'] - headmargin
		partial = availablewidth * pageratio
		scrapboard['bottom'] = pageheight/mm - headmargin - partial + separator / 2
		graphcoords['top'] = scrapboard['bottom'] - separator 



##################################################################
#
#   PDF section
#


# Load PDF object
def loadPDF(path):
	global pagewidth, pageheight, cm
	global myDialog

	if myDialog.orientation == 'portrait':
		if myDialog.pagesize == 'letter':
			pagewidth = letter[0]
			pageheight = letter[1]
		else:
			pagewidth = A4[0]
			pageheight = A4[1]
	else:
		if myDialog.pagesize == 'letter':
			pagewidth = letter[1]
			pageheight = letter[0]
		else:
			pagewidth = A4[1]
			pageheight = A4[0]
	
	return Canvas(path, pagesize = (pagewidth, pageheight))



def DrawText(font, fontsize, fontcolour, x, y, text):
	#print 'font', font
	pdf.setFont(font, fontsize)
	pdf.setFillColorCMYK(fontcolour[0], fontcolour[1], fontcolour[2], fontcolour[3])
	pdf.drawString(x, y, str(text))


def DrawTableLines(list, colour, thickness):

	from reportlab.graphics.shapes import Circle
	global myDialog

	for i, point in enumerate(list):

		try:
			drawline(list[i][1]*mm, list[i][2]*mm, list[i+1][1]*mm, list[i+1][2]*mm, colour, thickness, None)
		except:
			pass

		pdf.setFillColorCMYK(colour[0], colour[1], colour[2], colour[3])
		pdf.circle(point[1]*mm, point[2]*mm, thickness, 0, 1)
		
		if myDialog.drawpointsvalues == 1:
			DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, point[1]*mm + (thickness/6+1)*mm, point[2]*mm - (thickness/6+2.5)*mm, int(point[0]))


def DrawHeadlineIntoPage(text):

	drawrect(pagemargin['left']*mm, pageheight - pagemargin['top']*mm - headerheight*mm, pagewidth - pagemargin['right']*mm, pageheight - pagemargin['top']*mm, pdfcolour, None, 0, None, roundedcorners)
	DrawText(pdffont['Bold'], headlinefontsize, headlinefontcolour, 2*mm + pagemargin['left']*mm, 2.2*mm + pageheight - pagemargin['top']*mm - headerheight*mm, text)

def DrawMetrics(f, glyph, xoffset, yoffset, ratio):
	global myDialog
	g = Glyph(glyph)

	mywidth = g.width
	if mywidth == 0:
		mywidth = g.GetBoundingRect().width
		
	
	# Draw metrics
	if myDialog.drawmetrics == 1:
		# Versalhöhe
		drawline(xoffset*mm, yoffset*mm - descender(f)*ratio + capheight(f) * ratio, xoffset*mm + mywidth*ratio, yoffset*mm - descender(f)*ratio + capheight(f) * ratio, metricscolour, metricslinewidth, None)
		# x-Höhe
		drawline(xoffset*mm, yoffset*mm - descender(f)*ratio + xheight(f) * ratio, xoffset*mm + mywidth*ratio, yoffset*mm - descender(f)*ratio + xheight(f) * ratio, metricscolour, metricslinewidth, None)
		# Grundlinie
		drawline(xoffset*mm, yoffset*mm - descender(f)*ratio, xoffset*mm + mywidth*ratio, yoffset*mm - descender(f)*ratio, metricscolour, metricslinewidth, None)
		# Bounding Box
		drawrect(xoffset*mm, yoffset*mm - descender(f)*ratio + descender(f)*ratio, xoffset*mm + mywidth*ratio, yoffset*mm - descender(f)*ratio + ascender(f)*ratio, '', metricscolour, metricslinewidth, None, 0)

	# Draw guidelines
	if myDialog.drawguidelines == 1:

		# Local vertical guides
		for guide in g.vguides:
			try:
				a = (ascender(f)) * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = guide.position / mm * ratio
			y1 = (0 - descender(f)) / mm * ratio
			x2 = (guide.position + a) / mm * ratio
			y2 = (ascender(f) - descender(f)) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourguides, metricslinewidth, guidelinedashed)

		# Global vertical guides
		for guide in f.vguides:
			try:
				a = (ascender(f)) * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = guide.position / mm * ratio
			y1 = (0 - descender(f)) / mm * ratio
			x2 = (guide.position + a) / mm * ratio
			y2 = (ascender(f) - descender(f)) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourglobalguides, metricslinewidth, guidelinedashed)

		# Local horizontal guides
		for guide in g.hguides:
			try:
				a = g.width * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = 0
			y1 = (guide.position - descender(f)) / mm * ratio
			x2 = g.width / mm * ratio
			y2 = (guide.position - descender(f) + a) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourguides, metricslinewidth, guidelinedashed)

		# Global horizontal guides
		for guide in f.hguides:
			try:
				a = g.width * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = 0
			y1 = (guide.position - descender(f)) / mm * ratio
			x2 = g.width / mm * ratio
			y2 = (guide.position - descender(f) + a) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourglobalguides, metricslinewidth, guidelinedashed)

	# Draw font names under box
	if myDialog.fontnamesunderglyph == 1:
		DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, xoffset*mm + 2, yoffset*mm - 8, f.full_name)
#		output(f)


def PSCommandsFromGlyph(glyph):

	CommandsList = []

	for i, node in enumerate(glyph.nodes):

		if node.type == nOFF:
			CommandsList.append(('close', (node.x, node.y)))

		if node.type == nMOVE:
			CommandsList.append(('moveTo', (node.x, node.y)))

		if node.type == nLINE:
			CommandsList.append(('lineTo', (node.x, node.y)))

		if node.type == nCURVE:
			CurveCommandsList = []
			CurveCommandsList.append('curveTo')
			for point in node.points:
				CurveCommandsList.append( (point.x, point.y) )
			CommandsList.append(CurveCommandsList)

	return CommandsList

def ReturnPathObject(fillcolour, strokecolour, strokewidth, dashed):
	p = PDFPath()
	if fillcolour:
		p.fill = 1
		p.fillcolour = fillcolour
	else:
		p.fill = 0
	if strokecolour:
		p.stroke = 1
		p.strokecolour = strokecolour
		p.strokewidth = strokewidth
	else:
		p.stroke = 0
		p.strokewidth = 0
	if dashed:
		p.dashed = dashed
	return p



def DrawGlyph(f, glyph, PSCommands, xoffset, yoffset, ratio, fillcolour, strokecolour, strokewidth, dashed):

	global myDialog
	if not PSCommands:

		type = "glyph"

		# Copy glyph into memory (so remove overlap won't affect the current font)
		g = Glyph(glyph)
		if myDialog.outline == 'filled':
			output('RemoveOverlap()')
			g.RemoveOverlap()
	
		# Glyph has components.
		# Iterate through them and draw them first.
		if len(g.components) > 0:
			for component in g.components:
				DrawGlyph(f, component.Get(f), None, xoffset, yoffset, ratio, fillcolour, strokecolour, strokewidth, dashed)
	
		# Glyph has nodes of its own
		if len(g.nodes):
			PSCommands = PSCommandsFromGlyph(g)
			#print PSCommands
		else:
			PSCommands = ()
		
	else:
		type = "PScommands"


	if PSCommands:

		p = PDFPath()
		if fillcolour:
			p.fill = 1
			p.fillcolour = fillcolour
		else:
			p.fill = 0
		if strokecolour:
			p.stroke = 1
			p.strokecolour = strokecolour
			p.strokewidth = strokewidth
		else:
			p.stroke = 0
			p.strokewidth = 0
		if dashed:
			p.dashed = dashed		

		for command in PSCommands:
	
			if command[0] == 'moveTo':
				try:
					p.close()
				except:
					pass
	
				x = xoffset*mm + command[1][0] * ratio
				y = yoffset*mm + command[1][1] * ratio
				p.moveTo(x, y)
				#print "('moveTo', (%s, %s))," % (command[1][0], command[1][1])
	
			if command[0] == 'lineTo':
				x = xoffset*mm + command[1][0] * ratio
				y = yoffset*mm + command[1][1] * ratio
				p.lineTo(x, y)
				#print "('lineTo', (%s, %s))," % (command[1][0], command[1][1])
	
			if command[0] == 'curveTo':
	
				points = []
				#	pointsnaked = []
				#	print command[1]
				
				for point in command[1:]:
				#	print point
					points.append( (xoffset*mm + point[0] * ratio, yoffset*mm + point[1] * ratio) )
				#	pointsnaked.append( (point.x, point.y) )
				#print "('curveTo', %s)," % (pointsnaked)
				
				p.curveTo(points)
	
		p.close()
		p.draw()





######### draw primitives		

def drawline(x1, y1, x2, y2, colour, strokewidth, dashed):

	pdf.setStrokeColorCMYK(colour[0], colour[1], colour[2], colour[3])
	pdf.setLineWidth(strokewidth)
	if dashed:
		pdf.setDash(dashed[0], dashed[1])
	else:
		pdf.setDash(1)
	pdf.line(x1, y1, x2, y2)

def drawrect(x1, y1, x2, y2, fillcolour, strokecolour, strokewidth, dashed, rounded):

	if strokecolour:
		pdf.setStrokeColorCMYK(strokecolour[0], strokecolour[1], strokecolour[2], strokecolour[3])
	if strokewidth:
		pdf.setLineWidth(strokewidth)
		strokebool = 1
	else:
		strokebool = 0
	if dashed:
		pdf.setDash(dashed[0], dashed[1])
	else:
		pdf.setDash(1)

	if fillcolour:
		pdf.setFillColorCMYK(fillcolour[0], fillcolour[1], fillcolour[2], fillcolour[3])
		fillbool = 1
	else:
		pdf.setFillColorCMYK(0, 0, 0, 0)
		fillbool = 0

	pdf.roundRect(x1, y1, x2 - x1, y2 - y1, rounded, stroke = strokebool,  fill = fillbool)


##################################################################
#
#   FONTLAB related stuff
#

# collects font objects and sorts them in a specific manner
# return list of font objects
def collectfonts():

	fontlist = []
	
	for i in range(fl.count):
		fontlist.append(fl[i])
		
	return fontlist

# collects the glyphs that should be displayed
# and returns list of glyph names
def collectglyphnames():
	
	glyphlist = []
	
#	try:
#		glyphlist.append(fl.glyph.name)
#	except:
#		pass
	
	for g in fl.font.glyphs:
		if fl.Selected(g.index):
			glyphlist.append(g.name)

	return glyphlist

def capheight(f):
	return f.cap_height[0]

def xheight(f):
	return f.x_height[0]

def descender(f):
	return f.descender[0]

def ascender(f):
	return f.ascender[0]

def unicode2hex(u):
	return string.zfill(string.upper(hex(u)[2:]), 4)

errortexts = []
errors = 0

def raiseerror(text):
	global errors, errorslist
	errortexts.append(text)
	try:
		errors += 1
	except:
		errors = 1


def CheckForUpdates():
	if preferences['presets']['__default__']['checkforupdates']:
		import webbrowser, urllib
		try:
			if int(releasedate) < int(urllib.urlopen('http://www.yanone.de/typedesign/autopsy/latestreleasedate.txt').read()):
				x = fl.Message('Hey, I was reincarnated as a newer version.\nDo you want to connect to my download page on the internet?')
				if x == 1:
					webbrowser.open('http://www.yanone.de/typedesign/autopsy/download.php', 1, 1)
		except:
			pass # No network connection

##### MAIN

def main():

	global pdf
	global ratio
	global myDialog	
	global errors, errorstexts
	global glyphs	
	global reports

	CheckForUpdates()
	
	# Clear console
	if verbose:
		fl.output = ''
	output('-- main --')
	
  # Dialog stuff
	result = None
	NameList = []

	# Check, if fonts are present
	if fl.count < 1:
		raiseerror("No fonts open in FontLab.")
	else:
		# Check, if fonts have a full_name
		full_name_missing = 0
		for i in range(len(fl)):
			f = fl[i]
			if not f.full_name:
				full_name_missing += 1
		if full_name_missing:
			raiseerror("Some fonts don't have a 'Full Name'. Autopsy uses the 'Full Name' for handling fonts.\nPlease fill it out in the 'Font Info' window.")

		# Collect glyph names
		glyphs = collectglyphnames()
		if not glyphs:
			raiseerror("No glyphs selected.")
		
	
	# Initial sorting of fonts by width, weight

	widths_plain = '''Ultra-condensed	1
Compressed	1
Extra-condensed	2
Condensed	3
Semi-condensed	4
Narrow	4
Compact	4
Medium (normal)	5
Normal	5
Regular	5
Medium	5
Semi-extended	6
Wide	6
Semi-expanded	6
Expanded	7
Extended	7
Extra-extended	8
Extra-expanded	8
Ultra-expanded	9
Ultra-extended	9'''

	weights_plain = '''Thin	250
Hairline	250
Ultra Light	250
Micro	300
Extra Light	300
Fine	300
Slim	300
Dry	300
Clair	300
Skinny	300
Light	350
Semi Light	375
Plain	400
Gamma	400
Normal (Regular)	400
Regular	400
Book	450
News	450
Text	500
Medium	500
Beta	500
Median	500
DemiBold	500
SemiBold	500
Semi Bold	600
Alpha	600
Demi Bold	600
Bold	700
Boiled	700
Noir	700
Fett	700
Not That Fat	700
Extra Boiled	750
Extra Bold	750
Heavy	800
Mega	800
ExtraBold	800
Black	900
UltraBlack	900
Ultra Black	900
Fat	950
Ultra	1000
Super	1000
ExtraBlack	1000
Extra Black	1000'''
	
	# NOrmal mode
	if not errors:

		# Add fonts to NameList
		if fl.font[0].layers_number == 1:
			mode = 'normal'
		
			widths = Ddict(dict)
			for width in widths_plain.split("\n"):
				tmp = width.split("\t")
				widths[tmp[0]] = tmp[1]
		
			weights = Ddict(dict)
			for weight in weights_plain.split("\n"):
				tmp = weight.split("\t")
				weights[tmp[0]] = tmp[1]
		
			FontList = []
			for i in range(len(fl)):
				f = fl[i]
		
				# exclude MM
				if f[0].layers_number == 1:
		
					# width
					if f.width and f.width in widths:
						width = widths[f.width]
					else:
						width = 500
			
					# weights
					if f.weight_code > 0:
						weight = f.weight_code
					elif not f.weight_code and f.weight:
						for w in weights:
							if w == f.weight:
								weight = weights[w]
								break
					else:
						weight = 400
			
					# familyname
					if f.family_name:
						familyname = f.family_name
					else:
						familyname = '__default__'
							
					FontList.append((width, weight, f.full_name))
		
			FontList.sort()
		
			for listentry in FontList:
				NameList.append(listentry[2])
	
		# MM-mode
		elif fl.font[0].layers_number > 1:
			mode = 'MM'
			NameList.append(fl.font.full_name)


	# Some error handling
#	if not NameList:
#		raiseerror("No fonts open in FontLab.")

	
	# Call Dialog

	if NameList and not errors:
		myDialog = _listMultiSelect(mode, NameList)
		if myDialog.Run() == OK:
			NameList = myDialog.selection
			if NameList:
				result = []
				for anyName in NameList:
					if mode == 'normal':
						result.append(getFontByFullname(anyName))
					elif mode == 'MM':

						__list = anyName.split("/")
						_InstanceList = []
						for l in __list:
							try:
								_InstanceList.append(int(l))
							except:
								pass
						instance = Font(fl.font, _InstanceList)
						instance.full_name += ' ' + anyName
						result.append(instance)

			else: raiseerror("No fonts have been selected. I can't work like that.")
		#else: raiseerror("Canceled by user (That's you).")
		#del myDialog
#	elif not NameList:
#		raiseerror("No fonts open in FontLab.")

		try:
			fonts = result
		except:
			fonts = []
				
		if not myDialog.filename:
			raiseerror("No file name specified. Where do you expect me to save the file?.")



	
	if not errors and fonts and glyphs:
	
		starttime = time.time()

		# PDF Init stuff
		pdf = loadPDF(myDialog.filename)

	
	
		#############
		#
		# 	Collect information about the glyphs
		# 	
	
		# Dimensions
		reports = Ddict(dict)
	
		glyphwidth = Ddict(dict)
		maxwidthperglyph = Ddict(dict)
		maxwidth = 0
		maxsinglewidth = 0
		glyphheight = Ddict(dict)
		maxheightperglyph = Ddict(dict)
		maxheight = 0
		maxsingleheight = 0
		
		for glyph in glyphs:
	
			glyphwidth[glyph] = 0
			glyphheight[glyph] = 0
			maxwidthperglyph[glyph] = 0
			maxheightperglyph[glyph] = 0
			reports[glyph]['width'] = Report()
			reports[glyph]['height'] = Report()
			reports[glyph]['bboxwidth'] = Report()
			reports[glyph]['bboxheight'] = Report()
			reports[glyph]['highestpoint'] = Report()
			reports[glyph]['lowestpoint'] = Report()
			reports[glyph]['leftsidebearing'] = Report()
			reports[glyph]['rightsidebearing'] = Report()
			
			for i_f, font in enumerate(fonts):
	
				if font.has_key(glyph):
					g = font[glyph]
					glyphwidth[glyph] = g.width
					height = ascender(font) - descender(font)

					widthforgraph = glyphwidth[glyph]
					if widthforgraph == 0:
						widthforgraph = g.GetBoundingRect().width
					heightforgraph = height
	
					# width of kegel
					reports[glyph]['width'].addvalue((glyphwidth[glyph], widthforgraph, heightforgraph))
					# sum of widths per glyph
					if reports[glyph]['width'].sum > maxwidth:
						maxwidth = reports[glyph]['width'].sum
					if reports[glyph]['width'].max > maxsinglewidth:
						maxsinglewidth = reports[glyph]['width'].max
						
					# height of kegel
					glyphheight[glyph] = height
					reports[glyph]['height'].addvalue((glyphheight[glyph], widthforgraph, heightforgraph))
					# sum of heights per glyph
					if reports[glyph]['height'].sum > maxheight:
						maxheight = reports[glyph]['height'].sum
					if reports[glyph]['height'].max > maxsingleheight:
						maxsingleheight = reports[glyph]['height'].max
		
					# BBox
					overthetop = 20000
					
					bbox = g.GetBoundingRect()

					if bbox.width < -1*overthetop or bbox.width > overthetop:
						reports[glyph]['bboxwidth'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['bboxwidth'].addvalue((bbox.width, widthforgraph, heightforgraph))

					if bbox.height < -1*overthetop or bbox.height > overthetop:
						reports[glyph]['bboxheight'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['bboxheight'].addvalue((bbox.height, widthforgraph, heightforgraph))


					if (bbox.y + bbox.height) < -1*overthetop or (bbox.y + bbox.height) > overthetop:
						reports[glyph]['highestpoint'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['highestpoint'].addvalue((bbox.y + bbox.height, widthforgraph, heightforgraph))

					if bbox.y < -1*overthetop or bbox.y > overthetop:
						reports[glyph]['lowestpoint'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['lowestpoint'].addvalue((bbox.y, widthforgraph, heightforgraph))

					# L + R sidebearing
					reports[glyph]['leftsidebearing'].addvalue((bbox.x, widthforgraph, heightforgraph))
					reports[glyph]['rightsidebearing'].addvalue((glyphwidth[glyph] - bbox.width - bbox.x, widthforgraph, heightforgraph))



		# Recalculate drawing boards
		numberoftables = 0
		for table in availablegraphs:
			if eval('myDialog.graph_' + table):
				numberoftables += 1

		if numberoftables < 3:
			numberoftables = 3
		try:
			r = 2.0 / numberoftables
		except:
			r = .8
		SetScrapBoard(r)

			
		# Calculate ratio
		if myDialog.orientation == 'portrait':
			ratio = (scrapboard['top'] - scrapboard['bottom']) / maxheight * mm
			ratio2 = (scrapboard['right'] - scrapboard['left']) / maxsinglewidth * mm
			maxratio = 0.3
			if ratio > maxratio:
				ratio = maxratio
			if ratio > ratio2:
				ratio = ratio2
		else:
			ratio = (scrapboard['right'] - scrapboard['left']) / maxwidth * mm
			ratio2 = (scrapboard['top'] - scrapboard['bottom']) / maxsingleheight * mm
			maxratio = 0.3
			if ratio > maxratio:
				ratio = maxratio
			if ratio > ratio2:
				ratio = ratio2
	
	
	
	
		# Open Progress Bar
		tick = True
		fl.BeginProgress('%s working heavily on %s glyphs' % (programname, str(len(glyphs) * len(fonts))), len(glyphs) * len(fonts)) 


		# Draw front page
		output('-- font page --')

		xoffset = pagewidth/mm * 1/1.61
		yoffset = pageheight/mm * 1.61
		

		drawrect(-3*mm, -3*mm, pagewidth + 3*mm, pageheight + 3*mm, pdfcolour, None, None, None, 0)



		# Try to get a random glyph from a random font with nodes
		# try not more than 10000 times
		glyphfound = False

		randomfont = fonts[random.randint(0, len(fonts) - 1)]
		randomglyphindex = random.randint(0, len(randomfont) - 1)
		g = randomfont[randomglyphindex]

		if (g.nodes_number or g.components):
			glyphfound = True
		tries = 0
		while glyphfound == False and tries < 10000:
			randomfont = fonts[random.randint(0, len(fonts) - 1)]
			randomglyphindex = random.randint(0, len(randomfont) - 1)
			g = randomfont[randomglyphindex]
			if (g.nodes_number or g.components):
				glyphfound = True
			tries += 1
#		if (g.nodes or g.components):
#			glyphfound = True

		# if random didn't help, get first glyph with nodes
		if not glyphfound:
			for gi in range(len(fonts[0])):
				if fonts[0][gi].nodes_number or fonts[0][gi].components:
					g = fonts[0][gi]
			
		
		bbox = g.GetBoundingRect()
		localratio = .65 / bbox.height * (pageheight - yoffset)



		# draw logo and name
		logoyoffset = -5

		## YN
		ynlogo = [('moveTo', (350, 700)), ['curveTo', (0, 350), (138, 700), (0, 562)], ['curveTo', (350, 0), (0, 138), (138, 0)], ['curveTo', (700, 350), (562, 0), (700, 138)], ['curveTo', (350, 700), (700, 562), (562, 700)], ('moveTo', (548, 297)), ('lineTo', (542, 297)), ['curveTo', (536, 286), (536, 297), (536, 288)], ('lineTo', (536, 174)), ['curveTo', (510, 132), (536, 153), (531, 132)], ['curveTo', (481, 155), (496, 132), (489, 140)], ['curveTo', (416, 272), (481, 155), (435, 237)], ('lineTo', (416, 180)), ['curveTo', (422, 168), (416, 168), (420, 168)], ['curveTo', (434, 169), (425, 168), (430, 169)], ['curveTo', (451, 152), (444, 169), (451, 163)], ['curveTo', (430, 136), (451, 144), (445, 136)], ['curveTo', (399, 139), (421, 136), (413, 139)], ['curveTo', (365, 136), (386, 139), (374, 136)], ['curveTo', (345, 153), (350, 136), (345, 144)], ['curveTo', (362, 169), (345, 163), (352, 169)], ['curveTo', (374, 168), (366, 169), (371, 168)], ['curveTo', (380, 179), (376, 168), (380, 168)], ('lineTo', (380, 286)), ['curveTo', (374, 298), (380, 297), (376, 298)], ['curveTo', (362, 297), (371, 298), (368, 297)], ['curveTo', (347, 306), (355, 297), (350, 302)], ['curveTo', (332, 297), (345, 302), (340, 297)], ['curveTo', (320, 298), (326, 297), (326, 298)], ['curveTo', (316, 295), (319, 298), (318, 298)], ('lineTo', (261, 209)), ('lineTo', (261, 175)), ['curveTo', (267, 168), (261, 170), (263, 168)], ['curveTo', (281, 170), (270, 168), (274, 170)], ['curveTo', (296, 153), (291, 170), (296, 163)], ['curveTo', (275, 136), (296, 144), (291, 136)], ['curveTo', (241, 139), (262, 136), (254, 139)], ['curveTo', (208, 136), (228, 139), (221, 136)], ['curveTo', (188, 152), (194, 136), (188, 144)], ['curveTo', (205, 170), (188, 163), (195, 170)], ['curveTo', (217, 168), (211, 170), (212, 168)], ['curveTo', (223, 175), (219, 168), (223, 170)], ('lineTo', (223, 207)), ('lineTo', (168, 296)), ['curveTo', (164, 297), (167, 297), (165, 297)], ['curveTo', (153, 296), (160, 297), (158, 296)], ['curveTo', (134, 313), (139, 296), (134, 304)], ['curveTo', (152, 331), (134, 324), (141, 331)], ['curveTo', (186, 327), (165, 331), (175, 327)], ['curveTo', (215, 331), (197, 327), (203, 331)], ['curveTo', (234, 313), (229, 331), (234, 322)], ['curveTo', (213, 297), (234, 306), (230, 297)], ('lineTo', (212, 297)), ('lineTo', (243, 245)), ['curveTo', (273, 297), (251, 260), (267, 285)], ['curveTo', (268, 296), (270, 296), (268, 296)], ['curveTo', (249, 313), (254, 296), (249, 304)], ['curveTo', (268, 331), (249, 324), (256, 331)], ['curveTo', (298, 328), (275, 331), (287, 328)], ['curveTo', (332, 331), (308, 328), (322, 331)], ['curveTo', (348, 321), (339, 331), (345, 326)], ['curveTo', (365, 331), (350, 326), (356, 331)], ['curveTo', (389, 329), (369, 331), (378, 329)], ['curveTo', (413, 331), (399, 329), (406, 331)], ['curveTo', (431, 320), (428, 331), (430, 324)], ('lineTo', (433, 314)), ('lineTo', (500, 193)), ('lineTo', (500, 286)), ['curveTo', (490, 297), (500, 289), (500, 297)], ('lineTo', (482, 297)), ['curveTo', (465, 313), (472, 297), (465, 305)], ['curveTo', (486, 331), (465, 321), (471, 331)], ['curveTo', (516, 328), (496, 331), (504, 328)], ['curveTo', (547, 331), (526, 328), (536, 331)], ['curveTo', (566, 313), (561, 331), (566, 322)], ['curveTo', (548, 297), (566, 305), (561, 297)], ('moveTo', (359, 568)), ['curveTo', (422, 525), (385, 568), (408, 552)], ['curveTo', (486, 568), (436, 552), (459, 568)], ['curveTo', (544, 508), (518, 568), (544, 546)], ['curveTo', (422, 356), (544, 441), (472, 420)], ['curveTo', (301, 508), (372, 420), (301, 441)], ['curveTo', (359, 568), (301, 546), (326, 568)], ('moveTo', (206, 530)), ['curveTo', (193, 529), (202, 530), (197, 529)], ['curveTo', (176, 546), (183, 529), (176, 538)], ['curveTo', (197, 563), (176, 555), (182, 563)], ['curveTo', (231, 560), (209, 563), (216, 560)], ['curveTo', (264, 563), (244, 560), (252, 563)], ['curveTo', (284, 546), (278, 563), (284, 555)], ['curveTo', (268, 529), (284, 536), (275, 529)], ['curveTo', (255, 530), (263, 529), (260, 530)], ['curveTo', (249, 519), (253, 530), (249, 530)], ('lineTo', (249, 413)), ['curveTo', (255, 401), (249, 401), (253, 401)], ['curveTo', (268, 402), (259, 401), (263, 402)], ['curveTo', (284, 386), (277, 402), (284, 396)], ['curveTo', (264, 368), (284, 377), (278, 368)], ['curveTo', (232, 372), (248, 368), (244, 372)], ['curveTo', (196, 368), (217, 372), (215, 368)], ['curveTo', (176, 386), (182, 368), (176, 377)], ['curveTo', (193, 402), (176, 396), (183, 402)], ['curveTo', (206, 401), (198, 402), (201, 401)], ['curveTo', (211, 413), (207, 401), (211, 401)], ('lineTo', (211, 519)), ['curveTo', (206, 530), (211, 530), (207, 530)]]
		ynlogoring = [('moveTo', (350, 700)), ['curveTo', (0, 350), (138, 700), (0, 562)], ['curveTo', (350, 0), (0, 138), (138, 0)], ['curveTo', (700, 350), (562, 0), (700, 138)], ['curveTo', (350, 700), (700, 562), (562, 700)]]
		textyoffset = 0
		textxoffset = 0
		DrawGlyph(None, None, ynlogo, xoffset/mm - .5, 14.5 + logoyoffset, .05, headlinefontcolour, None, None, 1)
		DrawGlyph(None, None, ynlogoring, xoffset/mm - .5, 14.5 + logoyoffset, .05, None, (0,0,0,0), 3, (6,4))
		DrawText(pdffont['Regular'], 9, headlinefontcolour, textxoffset + xoffset + 15*mm, 22*mm + textyoffset + logoyoffset*mm, programname + ' ' + programversion + ' by Yanone')
		DrawText(pdffont['Regular'], 9, headlinefontcolour, textxoffset + xoffset + 15*mm, 18.4*mm + textyoffset + logoyoffset*mm, 'www.yanone.de/typedesign/autopsy/')

		## FSI
#		fsiwhite = [('moveTo', (483, 15)), ('lineTo', (1300, 15)), ('lineTo', (1300, 684)), ('lineTo', (483, 684))]
#		fsiyellow = [('moveTo', (17, 15)), ('lineTo', (479, 15)), ('lineTo', (479, 684)), ('lineTo', (17, 684))]
#		fsiblack = [('moveTo', (30, 671)), ('lineTo', (30, 29)), ('lineTo', (464, 29)), ('lineTo', (464, 671)), ('moveTo', (0, 700)), ('lineTo', (1322, 700)), ('lineTo', (1322, 0)), ('lineTo', (0, 0)), ('lineTo', (0, 700)), ('moveTo', (181, 225)), ['curveTo', (171, 183), (179, 215), (171, 191)], ['curveTo', (221, 162), (171, 159), (201, 162)], ('lineTo', (218, 150)), ['curveTo', (134, 152), (190, 150), (162, 152)], ['curveTo', (55, 150), (108, 152), (82, 150)], ('lineTo', (60, 162)), ['curveTo', (124, 220), (110, 159), (111, 179)], ('lineTo', (190, 446)), ['curveTo', (199, 490), (193, 455), (199, 480)], ['curveTo', (150, 509), (199, 513), (163, 509)], ('lineTo', (153, 522)), ['curveTo', (227, 519), (177, 521), (203, 519)], ['curveTo', (410, 522), (290, 519), (350, 521)], ('lineTo', (420, 431)), ('lineTo', (408, 431)), ['curveTo', (304, 509), (393, 497), (366, 510)], ['curveTo', (259, 506), (289, 509), (273, 508)], ('lineTo', (217, 358)), ('lineTo', (263, 358)), ['curveTo', (330, 416), (295, 358), (310, 370)], ('lineTo', (339, 416)), ('lineTo', (311, 274)), ('lineTo', (300, 274)), ['curveTo', (258, 346), (300, 310), (304, 346)], ('lineTo', (213, 346)), ('moveTo', (811, 508)), ['curveTo', (692, 545), (772, 531), (735, 545)], ['curveTo', (570, 433), (619, 545), (570, 500)], ['curveTo', (592, 370), (570, 409), (576, 388)], ['curveTo', (661, 337), (609, 354), (626, 348)], ('lineTo', (700, 325)), ['curveTo', (770, 253), (747, 311), (770, 288)], ['curveTo', (742, 198), (770, 231), (761, 212)], ['curveTo', (681, 181), (726, 186), (711, 181)], ['curveTo', (577, 215), (642, 181), (609, 191)], ('lineTo', (556, 178)), ['curveTo', (681, 143), (595, 155), (634, 143)], ['curveTo', (768, 169), (716, 143), (742, 151)], ['curveTo', (821, 260), (802, 190), (821, 225)], ['curveTo', (796, 329), (821, 284), (811, 311)], ['curveTo', (728, 367), (780, 347), (761, 356)], ('lineTo', (683, 381)), ['curveTo', (619, 444), (637, 395), (619, 413)], ['curveTo', (695, 508), (619, 482), (648, 508)], ['curveTo', (791, 473), (729, 508), (752, 499)], ('lineTo', (811, 508)), ('moveTo', (1017, 159)), ('lineTo', (1205, 159)), ('lineTo', (1205, 252)), ('lineTo', (1159, 252)), ('lineTo', (1159, 439)), ('lineTo', (1205, 439)), ('lineTo', (1205, 533)), ('lineTo', (1017, 533)), ('lineTo', (1017, 439)), ('lineTo', (1063, 439)), ('lineTo', (1063, 252)), ('lineTo', (1017, 252)), ('lineTo', (1017, 159)), ('moveTo', (1281, 667)), ('lineTo', (888, 667)), ('lineTo', (888, 33)), ('lineTo', (1281, 33)), ('lineTo', (1281, 667))]
#		textyoffset = 5
#		textxoffset = 30
#		DrawGlyph(None, None, fsiwhite, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,0,0,0), None, None, 1)
#		DrawGlyph(None, None, fsiyellow, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,.05,1,0), None, None, 1)
#		DrawGlyph(None, None, fsiblack, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,0,0,1), None, None, 1)
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 22*mm + textyoffset + logoyoffset*mm, programname + ' ' + programversion + ' by Yanone')
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 18.4*mm + textyoffset + logoyoffset*mm, 'www.yanone.de/typedesign/autopsy/')
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 14.8*mm + textyoffset + logoyoffset*mm, 'Licensed for FSI FontShop International GmbH')

		# Sample glyph
		DrawGlyph(fonts[0], g, None, xoffset/mm - bbox.x/mm*localratio, yoffset/mm - bbox.y/mm*localratio + 18, localratio, (0,0,0,0), headlinefontcolour, 3, (6, 4))

		# Autopsy Report
		DrawText(pdffont['Bold'], 48, headlinefontcolour, xoffset, yoffset, "Autopsy Report")

		# Other infos
		if myDialog.orientation == 'portrait':
			textmaxratio = 16000
		else:
			textmaxratio = 10000
		lines = []
		if len(fonts) > 1:
			patient = "Patients"
		else:
			patient = "Patient"
		lines.append((pdffont['Regular'], 18, headlinefontcolour, xoffset, 30, patient + ':'))
		yoffset -= 5
		for myfont in fonts:
			lines.append((pdffont['Bold'], 18, headlinefontcolour, xoffset, 20, str(myfont.full_name) + ' v' + str(myfont.version)))
		# get designers(s)
		designers = Ddict(dict)
		for f in fonts:
			if f.source:
				designers[f.source] = 1
			elif f.designer:
				designers[f.designer] = 1
			else:
				designers['Anonymous'] = 1
		if len(designers) > 1:
			doctor = 'Doctors'
		else:
			doctor = 'Doctor'
		fontinfos = {
		doctor : ", ".join(designers),
#		doctor : 'TypeDepartment of FontShop International',
		'Time' : time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
		}
		for fontinfo in fontinfos:
			lines.append((pdffont['Regular'], 18, headlinefontcolour, xoffset, 30, fontinfo + ':'))
			lines.append((pdffont['Bold'], 18, headlinefontcolour, xoffset, 20, fontinfos[fontinfo]))
		linesratio = 1.0/len(lines) * textmaxratio / pageheight/mm * 1.61
		if linesratio > 1:
			linesratio = 1
		for line in lines:
			yoffset -= line[4] * linesratio
			DrawText(line[0], line[1] * linesratio, line[2], line[3], yoffset, line[5])

		pdf.showPage()





		### MAIN PAGES ###


		for i, glyph in enumerate(glyphs):
			output('-- ' + glyph + ' --')
	
			if not tick:
				raiseerror('Aborted by user.')
				break
		
			glyphindex = fonts[0].FindGlyph(glyph)
	
			# Draw scrapboard into page
			if drawboards:
				drawrect(scrapboard['left']*mm, scrapboard['bottom']*mm, scrapboard['right']*mm, scrapboard['top']*mm, '', scrapboardcolour, metricslinewidth, None, 0)
				drawrect(graphcoords['left']*mm, graphcoords['bottom']*mm, graphcoords['right']*mm, graphcoords['top']*mm, '', scrapboardcolour, metricslinewidth, None, 0)
			
			try:
				unicodes = 'u' + string.join(map(unicode2hex, fonts[0][glyphindex].unicodes), "u u") + 'u'
			except:
				unicodes = ''
#			print '-', fonts[0][glyphindex], '-'
			DrawHeadlineIntoPage("/%s/ #%s# %s" % (glyph, glyphindex, unicodes))
	
			# Initial offset
	
			if myDialog.orientation == 'portrait':
				xoffsetinitial = scrapboard['left']
				yoffsetinitial = scrapboard['top'] - (ascender(fonts[0]) - descender(fonts[0])) / mm * ratio
			else:
				xoffsetinitial = scrapboard['left']
				yoffsetinitial = scrapboard['bottom']
	


			# Draw Metrics

			xoffset = xoffsetinitial
			yoffset = yoffsetinitial


			for i_f, font in enumerate(fonts):

				if font.has_key(glyph):
					g = font[glyph]
				elif not font.has_key(glyph) and fonts[i_f-1].has_key(glyph):
					g = fonts[i_f-1][glyph]			

				DrawMetrics(font, g, xoffset, yoffset, ratio)
	
				# increase offset
				if myDialog.orientation == 'portrait':
					yoffset -= (ascender(font) - descender(font)) / mm * ratio
				else:
					if g.width == 0:
						xoffset += g.GetBoundingRect().width / mm * ratio
					else:
						xoffset += g.width / mm * ratio
					


			# Draw Glyphs

			xoffset = xoffsetinitial
			yoffset = yoffsetinitial - descender(fonts[0])*ratio/mm

			for i_f, font in enumerate(fonts):

				# Glyph is in font
				if font.has_key(glyph):
					g = font[glyph]

				if myDialog.outline == 'filled':
					myglyphfillcolour = glyphcolour
					myglyphstrokecolour = None				
					myglyphstrokewidth = 0
					myglyphdashed = None
				elif myDialog.outline == 'xray':
					myglyphfillcolour = xrayfillcolour
					myglyphstrokecolour = glyphcolour				
					myglyphstrokewidth = 1.5
					myglyphdashed = None

	
				# Glyph is missing in font, draw replacement glyph
				elif not font.has_key(glyph) and fonts[i_f-1].has_key(glyph):
					g = fonts[i_f-1][glyph]			
					myglyphfillcolour = None
					myglyphstrokecolour = glyphcolour				
					myglyphstrokewidth = 1
					myglyphdashed = (3, 3)

				DrawGlyph(font, g, None, xoffset, yoffset, ratio, myglyphfillcolour, myglyphstrokecolour, myglyphstrokewidth, myglyphdashed)


	
				# increase offset
				if myDialog.orientation == 'portrait':
					yoffset -= (ascender(font) - descender(font)) / mm * ratio
				else:
					if g.width == 0:
						xoffset += g.GetBoundingRect().width / mm * ratio
					else:
						xoffset += g.width / mm * ratio


				tick = fl.TickProgress((i) * len(fonts) + i_f + 1)
	
	
			# Aggregate graph objects into a list
	
			tableobjects = []
			for table in availablegraphs:
				if eval('myDialog.graph_' + table):
					reports[glyph][table].glyphname = glyph
					reports[glyph][table].graphname = table
					reports[glyph][table].drawpointsvalues = myDialog.drawpointsvalues

					reports[glyph][table].scope = eval('myDialog.graph_' + table + '_scope')

					if graphcolour.has_key(table):
						reports[glyph][table].strokecolour = graphcolour[table]
					else:
						reports[glyph][table].strokecolour = graphcolour['__default__']
					tableobjects.append(reports[glyph][table])
		
		
			# Calculate bbox for graphs an draw them

			for t, table in enumerate(tableobjects):
	
				if myDialog.orientation == 'portrait':
					tablewidth = ((graphcoords['right'] - graphcoords['left']) - (tableseparator * (len(tableobjects) - 1))) / len(tableobjects)
					tableheight = reports[glyph]['height'].sum/mm*ratio
					table.left = graphcoords['left'] + t * (tablewidth + tableseparator)
					table.right = table.left + tablewidth
					table.top = graphcoords['top']
					table.bottom = table.top - tableheight
				else:
					if reports[glyph]['width']:
						tablewidth = reports[glyph]['width'].sum/mm*ratio
					else:
						tablewidth = reports[glyph]['bboxwidth'].sum/mm*ratio
					tableheight = ((graphcoords['top'] - graphcoords['bottom']) - (tableseparator * (len(tableobjects) - 1))) / len(tableobjects)
					table.left = graphcoords['left']
					table.right = table.left + tablewidth
					table.top = graphcoords['top'] - t * (tableheight + tableseparator)
					table.bottom = table.top - tableheight
				
				table.draw()

			# PDF Bookmarks
			pdf.bookmarkPage(glyph)
			pdf.addOutlineEntry(None, glyph, 0, 0)

			# End page
			pdf.showPage()
	
	
		# PDF save stuff
		try:
			pdf.save()
		except:
			raiseerror("%s has no write access to the file %s. Maybe the file is opened by another application?" % (programname, myDialog.filename))
		output("time: " + str(time.time() - starttime) + "sec, ca." + str((time.time() - starttime) / len(glyphs)) + "sec per glyph")
	
		fl.EndProgress()
	


	if errors:
		for error in errortexts:
			
			dlg = Message(error, programname)
			
	if not errors and fonts and myDialog.openPDF:
		launchfile(myDialog.filename)
			


def launchfile(path):
	if os.path.exists(path):
		if os.name == 'posix':
			os.system('open "%s"' % path)
		elif os.name == 'nt':
			os.startfile('"' + path + '"')

def findFlsPath(*requestedPath):
	requestedPath = os.path.join(*requestedPath)
	try:    folders = [fl.path, fl.commonpath, fl.userpath, fl.usercommonpath]
	except: folders = [fl.path]
	for folder in folders:
		thePath = os.path.join(folder,requestedPath)
		if os.path.exists(thePath):
			return thePath
	return None









# Settings

def LoadSettings():
	global preferences

		# Default values, if plist does not yet exist
	defaultpreferences = Ddict(dict)

	# User path
	defaultpdf = ''
	if os.path.exists(os.path.join(os.path.expanduser('~'), 'Desktop')):
		defaultpdf = os.path.join(os.path.expanduser('~'), 'Desktop', 'Autopsy.pdf')


	defaultpreferences['presets']['__default__'] = {
		'orientation': 'landscape',
		'pagesize': 'a4',
		'outline': 'filled',
		# Other
		'drawpointsvalues': 1,
		'drawmetrics': 1,
		'drawguidelines': 1,
		'fontnamesunderglyph': 0,
		'filename': defaultpdf,
		'openPDF': 1,
		'checkforupdates': 1,
		# Graphs
		'graph_width': 1,
		'graph_width_scope': 'local',
		'graph_bboxwidth': 0,
		'graph_bboxwidth_scope': 'local',
		'graph_bboxheight': 0,
		'graph_bboxheight_scope': 'local',
		'graph_highestpoint': 0,
		'graph_highestpoint_scope': 'global',
		'graph_lowestpoint': 0,
		'graph_lowestpoint_scope': 'global',
		'graph_leftsidebearing': 0,
		'graph_leftsidebearing_scope': 'local',
		'graph_rightsidebearing': 0,
		'graph_rightsidebearing_scope': 'local',
		}

	# Load prefs from plist
	preferences = Ddict(dict)
	preferences['presets'] = Ddict(dict)
	preferences['presets']['__default__'] = Ddict(dict)
	if findFlsPath('Macros', programname + '.plist'):
	#	print 'plist found'
	#if os.path.exists(os.path.join(fl.path, 'Macros', programname + '.plist')):
		preferences = readPlist(findFlsPath('Macros', programname + '.plist'))
#	else:
#		print 'plist fnot ound'


	# Apply default prefs to loaded plist-prefs, if they don't exist
	for pref in defaultpreferences['presets']['__default__']:
		#print defaultpreferences['presets']['__default__'][pref]
		if not preferences['presets']['__default__'].has_key(pref):
			preferences['presets']['__default__'][pref] = defaultpreferences['presets']['__default__'][pref]

	preferences['version'] = programversion


	# Load Custom fonts
	if preferences.has_key('appearance'):

		# Set Custom fonts
		if preferences['appearance'].has_key('customfontfolder') and preferences['appearance'].has_key('customfontRegularAFM') and preferences['appearance'].has_key('customfontRegularPFB') and preferences['appearance'].has_key('customfontBoldAFM') and preferences['appearance'].has_key('customfontBoldPFB'):
			if preferences['appearance']['customfontRegularName'] == preferences['appearance']['customfontBoldName']:
				RegisterPFBFont('CustomRegular', preferences['appearance']['customfontRegularName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularAFM'], preferences['appearance']['customfontRegularPFB'])
				pdffont['Regular'] = 'CustomRegular'
				pdffont['Bold'] = 'CustomRegular'
			else:
				RegisterPFBFont('CustomRegular', preferences['appearance']['customfontRegularName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularAFM'], preferences['appearance']['customfontRegularPFB'])
				RegisterPFBFont('CustomBold', preferences['appearance']['customfontBoldName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontBoldAFM'], preferences['appearance']['customfontBoldPFB'])
				pdffont['Regular'] = 'CustomRegular'
				pdffont['Bold'] = 'CustomBold'
		elif preferences['appearance'].has_key('customfontfolder') and preferences['appearance'].has_key('customfontRegularTTF') and preferences['appearance'].has_key('customfontBoldTTF'):
			if preferences['appearance']['customfontRegularTTF'] == preferences['appearance']['customfontBoldTTF']:
				RegisterTTFont('CustomRegular', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularTTF'])
				pdffont['Regular'] = 'CustomRegular'
				pdffont['Bold'] = 'CustomRegular'
			else:
				RegisterTTFont('CustomRegular', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularTTF'])
				RegisterTTFont('CustomBold', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontBoldTTF'])
				pdffont['Regular'] = 'CustomRegular'
				pdffont['Bold'] = 'CustomBold'

		# Set custom colour	
		if preferences['appearance'].has_key('colour'):
			global pdfcolour
			pdfcolour = preferences['appearance']['colour']
	
#	preferences['appearance']['colour'] = (0,0.05,1,0)


def SaveSettings():
	global preferences
	if findFlsPath('Macros', programname + '.plist'): preffile = findFlsPath('Macros', programname + '.plist')
	else: preffile = os.path.join(findFlsPath('Macros'), programname + '.plist')
	writePlist(preferences, preffile)

def RegisterTTFont(internalname, folder, ttf):
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
	pdfmetrics.registerFont(TTFont(internalname, os.path.join(folder, ttf)))

def RegisterPFBFont(internalname, fullname, folder, afm, pfb):
	from reportlab.pdfbase import pdfmetrics
	newfontface = pdfmetrics.EmbeddedType1Face(os.path.join(folder, afm), os.path.join(folder, pfb))
	pdfmetrics.registerTypeFace(newfontface)
	newfont = pdfmetrics.Font(internalname, fullname, 'WinAnsiEncoding')
	pdfmetrics.registerFont(newfont)




#####################
#
#  Dialogs
#


class Message:
	def __init__(self, message, title):

	### Start auto-generated code ###
		# The main dialog window
		self.d = Dialog(self)
		self.d.size = Point( 382,  138)
		self.d.Center()
		self.d.title = title
		self.d.AddControl(STATICCONTROL, Rect( 15,  15,  367,  103), 'message', STYLE_LABEL, '')
		self.message = message
		self.d.Run()



class _listMultiSelect:
	def __init__(self, mode, OptList=None):
		
		title = programname + ' ' + programversion
		self.mode = mode
		self.OptList = OptList

	### Start auto-generated code ###
		# The main dialog window
		self.d = Dialog(self)
		self.d.size = Point( 621,  610)
		self.d.Center()
		self.d.title = title
		self.d.AddControl(STATICCONTROL, Rect( 15,  455,  191,  471), 'Label2', STYLE_LABEL, 'Page size')

		if mode == 'normal':
			self.d.AddControl(STATICCONTROL, Rect( 15,  215,  191,  231), 'Label3', STYLE_LABEL, 'Fonts in FontLab')
			self.d.AddControl(LISTCONTROL, Rect( 15,  231,  239,  447), 'List_opt', STYLE_LIST, '')
			self.d.AddControl(LISTCONTROL, Rect( 311,  231,  535,  447), 'List_sel', STYLE_LIST, '')
			self.d.AddControl(STATICCONTROL, Rect( 311,  215,  487,  231), 'Label4', STYLE_LABEL, 'Use these fonts')
			self.d.AddControl(BUTTONCONTROL, Rect( 247,  231,  303,  263), 'add_one', STYLE_BUTTON, '>')
			self.d.AddControl(BUTTONCONTROL, Rect( 247,  271,  303,  303), 'add_all', STYLE_BUTTON, '>>')
			self.d.AddControl(BUTTONCONTROL, Rect( 247,  311,  303,  343), 'rem_one', STYLE_BUTTON, '<')
			self.d.AddControl(BUTTONCONTROL, Rect( 247,  351,  303,  383), 'rem_all', STYLE_BUTTON, '<<')
#			self.d.AddControl(BUTTONCONTROL, Rect( 247,  391,  303,  423), 'addfonts', STYLE_BUTTON, 'R')
			self.d.AddControl(BUTTONCONTROL, Rect( 543,  272,  599,  304), 'move_dn', STYLE_BUTTON, 'down')
			self.d.AddControl(BUTTONCONTROL, Rect( 543,  231,  599,  263), 'move_up', STYLE_BUTTON, 'up')
		elif mode == 'MM':
			self.d.AddControl(STATICCONTROL, Rect( 15,  215,  559,  231), 'Label3', STYLE_LABEL, 'Values for ' + str(OptList[0]) + ' Multiple Master instances')
			self.d.AddControl(EDITCONTROL, Rect( 15,  231,  559,  aAUTO), 'MMvalues', STYLE_EDIT, '')
		
		self.d.AddControl(STATICCONTROL, Rect( 15,  495,  287,  511), 'Label5', STYLE_LABEL, 'Path to PDF (will overwrite without asking)')
		self.d.AddControl(EDITCONTROL, Rect( 15,  512,  559,  aAUTO), 'filename', STYLE_EDIT, '')
		self.d.AddControl(BUTTONCONTROL, Rect( 567,  507,  599,  539), 'browse_file', STYLE_BUTTON, '...')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 87,  471,  180,  490), 'pagesize_letter', STYLE_CHECKBOX, 'Letter')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  471,  80,  490), 'pagesize_a4', STYLE_CHECKBOX, 'A4')

		# Page Orientation
#		self.d.AddControl(STATICCONTROL, Rect( 15,  15,  191,  31), 'Label1', STYLE_LABEL, 'Page Orientation')
#		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  31,  100,  50), 'orientation_portrait', STYLE_CHECKBOX, 'Portrait')
#		self.d.AddControl(CHECKBOXCONTROL, Rect( 107,  31,  200,  50), 'orientation_landscape', STYLE_CHECKBOX, 'Landscape')
		self.d.AddControl(STATICCONTROL, Rect( 15,  33,  191,  52), 'Label1', STYLE_LABEL, 'Orientation')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 107,  31,  190,  50), 'orientation_portrait', STYLE_CHECKBOX, 'Portrait')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 190,  31,  300,  50), 'orientation_landscape', STYLE_CHECKBOX, 'Landscape')

		# Outline mode
		self.d.AddControl(STATICCONTROL, Rect( 15,  81,  191,  100), 'Label1', STYLE_LABEL, 'Glyph outline')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 107,  79,  180,  98), 'outline_filled', STYLE_CHECKBOX, 'filled')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 190,  79,  300,  98), 'outline_xray', STYLE_CHECKBOX, 'X-RAY')

		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  103,  230,  122), 'drawmetrics', STYLE_CHECKBOX, 'Draw metrics')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  127,  230,  146), 'drawguidelines', STYLE_CHECKBOX, 'Draw guidelines')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  151,  230,  170), 'drawpointsvalues', STYLE_CHECKBOX, 'Draw graph values')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  175,  230,  194), 'fontnamesunderglyph', STYLE_CHECKBOX, 'Fontnames under glyph')

		self.d.AddControl(CHECKBOXCONTROL, Rect( 15,  538,  206,  557), 'openPDF', STYLE_CHECKBOX, 'Open PDF in Reader')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  538,  580,  557), 'checkforupdates', STYLE_CHECKBOX, 'Check online for updates (on start)')
		
		if findFlsPath('Macros', 'Autopsy User Guide.pdf'):
		#if os.path.exists(os.path.join(fl.path, 'Macros', 'Autopsy User Guide.pdf')):
			self.d.AddControl(BUTTONCONTROL, Rect( 543,  15,  599,  47), 'user_guide', STYLE_BUTTON, '?')
		
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  31,  450,  50), 'graph_width_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  31,  474,  50), 'graph_width_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(STATICCONTROL, Rect( 416,  15,  456,  31), 'Label7', STYLE_LABEL, 'Local')
		self.d.AddControl(STATICCONTROL, Rect( 455,  15,  495,  31), 'Label8', STYLE_LABEL, 'Global')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  31,  407,  50), 'graph_width', STYLE_CHECKBOX, 'Width')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  55,  424,  74), 'graph_bboxwidth', STYLE_CHECKBOX, 'BBox Width')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  55,  450,  74), 'graph_bboxwidth_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  55,  474,  74), 'graph_bboxwidth_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  79,  424,  98), 'graph_bboxheight', STYLE_CHECKBOX, 'BBox Height')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  79,  450,  98), 'graph_bboxheight_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  79,  474,  98), 'graph_bboxheight_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(STATICCONTROL, Rect( 311,  15,  407,  31), 'Label9', STYLE_LABEL, 'Graphs')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  127,  424,  146), 'graph_lowestpoint', STYLE_CHECKBOX, 'BBox Lowest')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  103,  424,  122), 'graph_highestpoint', STYLE_CHECKBOX, 'BBox Highest')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  103,  450,  122), 'graph_highestpoint_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  103,  474,  122), 'graph_highestpoint_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  127,  450,  146), 'graph_lowestpoint_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  127,  474,  146), 'graph_lowestpoint_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  175,  424,  194), 'graph_rightsidebearing', STYLE_CHECKBOX, 'R Sidebearing')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 311,  151,  424,  170), 'graph_leftsidebearing', STYLE_CHECKBOX, 'L Sidebearing')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  151,  450,  170), 'graph_leftsidebearing_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  151,  474,  170), 'graph_leftsidebearing_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 431,  175,  450,  194), 'graph_rightsidebearing_scope_local', STYLE_CHECKBOX, '')
		self.d.AddControl(CHECKBOXCONTROL, Rect( 455,  175,  474,  194), 'graph_rightsidebearing_scope_global', STYLE_CHECKBOX, '')
		self.d.AddControl(STATICCONTROL, Rect( 15,  567,  439,  583), 'Label10', STYLE_LABEL, 'Autopsy 1.1 by Yanone. Free under GPLv3.')

		if mode == 'MM': 
			self.customdata = Ddict(dict)
			self.MMvalues = ''
			self.MMfont = getFontByFullname(OptList[0])
			if self.MMfont.has_key('.notdef'):
				if self.MMfont['.notdef'].customdata:
					self.customdata = readPlistFromString(self.MMfont['.notdef'].customdata)
					self.MMvalues = self.customdata['MMinstances']
					

		self.drawpointsvalues = preferences['presets']['__default__']['drawpointsvalues']
		self.drawmetrics = preferences['presets']['__default__']['drawmetrics']
		self.drawguidelines = preferences['presets']['__default__']['drawguidelines']
		self.fontnamesunderglyph = preferences['presets']['__default__']['fontnamesunderglyph']
		self.filename = preferences['presets']['__default__']['filename']
		self.openPDF = preferences['presets']['__default__']['openPDF']
		self.checkforupdates = preferences['presets']['__default__']['checkforupdates']
		
		# Orientation
		if preferences['presets']['__default__']['orientation'] == 'landscape':
			self.orientation_landscape = 1
			self.orientation_portrait = 0
		elif preferences['presets']['__default__']['orientation'] == 'portrait':
			self.orientation_landscape = 0
			self.orientation_portrait = 1
		self.orientation = preferences['presets']['__default__']['orientation']

		# Outline mode
		if preferences['presets']['__default__']['outline'] == 'filled':
			self.outline_filled = 1
			self.outline_xray = 0
		elif preferences['presets']['__default__']['outline'] == 'xray':
			self.outline_filled = 0
			self.outline_xray = 1
		self.outline = preferences['presets']['__default__']['outline']

		# Page size
		if preferences['presets']['__default__']['pagesize'] == 'a4':
			self.pagesize_a4 = 1
			self.pagesize_letter = 0
		elif preferences['presets']['__default__']['pagesize'] == 'letter':
			self.pagesize_a4 = 0
			self.pagesize_letter = 1
		self.pagesize = preferences['presets']['__default__']['pagesize']

		# Graphs
		
		# Width
		self.graph_width = preferences['presets']['__default__']['graph_width']
		if preferences['presets']['__default__']['graph_width_scope'] == 'local':
			self.graph_width_scope_local = 1
			self.graph_width_scope_global = 0
		elif preferences['presets']['__default__']['graph_width_scope'] == 'global':
			self.graph_width_scope_local = 0
			self.graph_width_scope_global = 1
		self.graph_width_scope = preferences['presets']['__default__']['graph_width_scope']
		# BBox width
		self.graph_bboxwidth = preferences['presets']['__default__']['graph_bboxwidth']
		if preferences['presets']['__default__']['graph_bboxwidth_scope'] == 'local':
			self.graph_bboxwidth_scope_local = 1
			self.graph_bboxwidth_scope_global = 0
		elif preferences['presets']['__default__']['graph_bboxwidth_scope'] == 'global':
			self.graph_bboxwidth_scope_local = 0
			self.graph_bboxwidth_scope_global = 1
		self.graph_bboxwidth_scope = preferences['presets']['__default__']['graph_bboxwidth_scope']
		# BBox height
		self.graph_bboxheight = preferences['presets']['__default__']['graph_bboxheight']
		if preferences['presets']['__default__']['graph_bboxheight_scope'] == 'local':
			self.graph_bboxheight_scope_local = 1
			self.graph_bboxheight_scope_global = 0
		elif preferences['presets']['__default__']['graph_bboxheight_scope'] == 'global':
			self.graph_bboxheight_scope_local = 0
			self.graph_bboxheight_scope_global = 1
		self.graph_bboxheight_scope = preferences['presets']['__default__']['graph_bboxheight_scope']
		# highestpoint
		self.graph_highestpoint = preferences['presets']['__default__']['graph_highestpoint']
		if preferences['presets']['__default__']['graph_highestpoint_scope'] == 'local':
			self.graph_highestpoint_scope_local = 1
			self.graph_highestpoint_scope_global = 0
		elif preferences['presets']['__default__']['graph_highestpoint_scope'] == 'global':
			self.graph_highestpoint_scope_local = 0
			self.graph_highestpoint_scope_global = 1
		self.graph_highestpoint_scope = preferences['presets']['__default__']['graph_highestpoint_scope']
		# lowestpoint
		self.graph_lowestpoint = preferences['presets']['__default__']['graph_lowestpoint']
		if preferences['presets']['__default__']['graph_lowestpoint_scope'] == 'local':
			self.graph_lowestpoint_scope_local = 1
			self.graph_lowestpoint_scope_global = 0
		elif preferences['presets']['__default__']['graph_lowestpoint_scope'] == 'global':
			self.graph_lowestpoint_scope_local = 0
			self.graph_lowestpoint_scope_global = 1
		self.graph_lowestpoint_scope = preferences['presets']['__default__']['graph_lowestpoint_scope']
		# leftsidebearing
		self.graph_leftsidebearing = preferences['presets']['__default__']['graph_leftsidebearing']
		if preferences['presets']['__default__']['graph_leftsidebearing_scope'] == 'local':
			self.graph_leftsidebearing_scope_local = 1
			self.graph_leftsidebearing_scope_global = 0
		elif preferences['presets']['__default__']['graph_leftsidebearing_scope'] == 'global':
			self.graph_leftsidebearing_scope_local = 0
			self.graph_leftsidebearing_scope_global = 1
		self.graph_leftsidebearing_scope = preferences['presets']['__default__']['graph_leftsidebearing_scope']
		# rightsidebearing
		self.graph_rightsidebearing = preferences['presets']['__default__']['graph_rightsidebearing']
		if preferences['presets']['__default__']['graph_rightsidebearing_scope'] == 'local':
			self.graph_rightsidebearing_scope_local = 1
			self.graph_rightsidebearing_scope_global = 0
		elif preferences['presets']['__default__']['graph_rightsidebearing_scope'] == 'global':
			self.graph_rightsidebearing_scope_local = 0
			self.graph_rightsidebearing_scope_global = 1
		self.graph_rightsidebearing_scope = preferences['presets']['__default__']['graph_rightsidebearing_scope']

		self.addfonts()

		# Check for previously loaded fonts and append to the option list
		if mode == 'normal' and preferences['presets']['__default__'].has_key('fontselection'):
			for i, sel in enumerate(preferences['presets']['__default__']['fontselection']):
				if sel in self.List_opt:
					self.List_sel.append(sel)
					self.List_opt.remove(sel)

	def addfonts(self):
		self.List_opt = self.OptList
		self.List_sel = []
		self.d.PutValue('List_opt')
		self.d.PutValue('List_sel')
		self.selection = []
		self.List_opt_index = 0
		self.List_sel_index = -1
		self.checkLists()

	# Grouping of checkboxes

	def on_pagesize_letter(self, code):
		self.pagesize_letter = 1
		self.d.PutValue('pagesize_letter')
		self.pagesize_a4 = 0
		self.d.PutValue('pagesize_a4')
		self.pagesize = 'letter'

	def on_pagesize_a4(self, code):
		self.pagesize_a4 = 1
		self.d.PutValue('pagesize_a4')
		self.pagesize_letter = 0
		self.d.PutValue('pagesize_letter')
		self.pagesize = 'a4'

	def on_outline_filled(self, code):
		self.outline_filled = 1
		self.d.PutValue('outline_filled')
		self.outline_xray = 0
		self.d.PutValue('outline_xray')
		self.outline = 'filled'

	def on_outline_xray(self, code):
		self.outline_xray = 1
		self.d.PutValue('outline_xray')
		self.outline_filled = 0
		self.d.PutValue('outline_filled')
		self.outline = 'xray'

	def on_orientation_landscape(self, code):
		self.orientation_landscape = 1
		self.d.PutValue('orientation_landscape')
		self.orientation_portrait = 0
		self.d.PutValue('orientation_portrait')
		self.orientation = 'landscape'

	def on_orientation_portrait(self, code):
		self.orientation_portrait = 1
		self.d.PutValue('orientation_portrait')
		self.orientation_landscape = 0
		self.d.PutValue('orientation_landscape')
		self.orientation = 'portrait'

	def on_graph_width_scope_local(self, code):
		self.graph_width_scope_local = 1
		self.d.PutValue('graph_width_scope_local')
		self.graph_width_scope_global = 0
		self.d.PutValue('graph_width_scope_global')
		self.graph_width_scope = 'local'

	def on_graph_width_scope_global(self, code):
		self.graph_width_scope_global = 1
		self.d.PutValue('graph_width_scope_global')
		self.graph_width_scope_local = 0
		self.d.PutValue('graph_width_scope_local')
		self.graph_width_scope = 'global'

	def on_graph_bboxwidth_scope_local(self, code):
		self.graph_bboxwidth_scope_local = 1
		self.d.PutValue('graph_bboxwidth_scope_local')
		self.graph_bboxwidth_scope_global = 0
		self.d.PutValue('graph_bboxwidth_scope_global')
		self.graph_bboxwidth_scope = 'local'

	def on_graph_bboxwidth_scope_global(self, code):
		self.graph_bboxwidth_scope_global = 1
		self.d.PutValue('graph_bboxwidth_scope_global')
		self.graph_bboxwidth_scope_local = 0
		self.d.PutValue('graph_bboxwidth_scope_local')
		self.graph_bboxwidth_scope = 'global'

	def on_graph_bboxheight_scope_local(self, code):
		self.graph_bboxheight_scope_local = 1
		self.d.PutValue('graph_bboxheight_scope_local')
		self.graph_bboxheight_scope_global = 0
		self.d.PutValue('graph_bboxheight_scope_global')
		self.graph_bboxheight_scope = 'local'

	def on_graph_bboxheight_scope_global(self, code):
		self.graph_bboxheight_scope_global = 1
		self.d.PutValue('graph_bboxheight_scope_global')
		self.graph_bboxheight_scope_local = 0
		self.d.PutValue('graph_bboxheight_scope_local')
		self.graph_bboxheight_scope = 'global'

	def on_graph_highestpoint_scope_local(self, code):
		self.graph_highestpoint_scope_local = 1
		self.d.PutValue('graph_highestpoint_scope_local')
		self.graph_highestpoint_scope_global = 0
		self.d.PutValue('graph_highestpoint_scope_global')
		self.graph_highestpoint_scope = 'local'

	def on_graph_highestpoint_scope_global(self, code):
		self.graph_highestpoint_scope_global = 1
		self.d.PutValue('graph_highestpoint_scope_global')
		self.graph_highestpoint_scope_local = 0
		self.d.PutValue('graph_highestpoint_scope_local')
		self.graph_highestpoint_scope = 'global'

	def on_graph_lowestpoint_scope_local(self, code):
		self.graph_lowestpoint_scope_local = 1
		self.d.PutValue('graph_lowestpoint_scope_local')
		self.graph_lowestpoint_scope_global = 0
		self.d.PutValue('graph_lowestpoint_scope_global')
		self.graph_lowestpoint_scope = 'local'

	def on_graph_lowestpoint_scope_global(self, code):
		self.graph_lowestpoint_scope_global = 1
		self.d.PutValue('graph_lowestpoint_scope_global')
		self.graph_lowestpoint_scope_local = 0
		self.d.PutValue('graph_lowestpoint_scope_local')
		self.graph_lowestpoint_scope = 'global'

	def on_graph_leftsidebearing_scope_local(self, code):
		self.graph_leftsidebearing_scope_local = 1
		self.d.PutValue('graph_leftsidebearing_scope_local')
		self.graph_leftsidebearing_scope_global = 0
		self.d.PutValue('graph_leftsidebearing_scope_global')
		self.graph_leftsidebearing_scope = 'local'

	def on_graph_leftsidebearing_scope_global(self, code):
		self.graph_leftsidebearing_scope_global = 1
		self.d.PutValue('graph_leftsidebearing_scope_global')
		self.graph_leftsidebearing_scope_local = 0
		self.d.PutValue('graph_leftsidebearing_scope_local')
		self.graph_leftsidebearing_scope = 'global'

	def on_graph_rightsidebearing_scope_local(self, code):
		self.graph_rightsidebearing_scope_local = 1
		self.d.PutValue('graph_rightsidebearing_scope_local')
		self.graph_rightsidebearing_scope_global = 0
		self.d.PutValue('graph_rightsidebearing_scope_global')
		self.graph_rightsidebearing_scope = 'local'

	def on_graph_rightsidebearing_scope_global(self, code):
		self.graph_rightsidebearing_scope_global = 1
		self.d.PutValue('graph_rightsidebearing_scope_global')
		self.graph_rightsidebearing_scope_local = 0
		self.d.PutValue('graph_rightsidebearing_scope_local')
		self.graph_rightsidebearing_scope = 'global'


	### End auto-generated code ###
					

	def checkLists(self):
		self.d.GetValue('List_opt')
		self.d.GetValue('List_sel')
		if self.List_opt:
			self.d.Enable('add_one', 1)
			self.d.Enable('add_all', 1)
			if self.List_opt_index == -1:
				self.List_opt_index = len(self.List_opt) - 1
		else:
			self.d.Enable('add_one', 0)
			self.d.Enable('add_all', 0)
		if self.List_sel:
			self.d.Enable('rem_one', 1)
			self.d.Enable('rem_all', 1)
			if self.List_sel_index == -1:
				self.List_sel_index = len(self.List_sel) - 1
			self.d.Enable('move_up', 1)
			self.d.Enable('move_dn', 1)
		else:
			self.d.Enable('rem_one', 0)
			self.d.Enable('rem_all', 0)
			self.d.Enable('move_up', 0)
			self.d.Enable('move_dn', 0)

	def on_List_opt(self, code):
		self.d.GetValue('List_opt')
#		log.debug('_listMultiSelect.on_List_opt %d', self.List_opt_index)

	def on_List_opt_index(self, code):
		self.d.GetValue('List_opt')
#		log.debug('_listMultiSelect.List_opt_index %d', self.List_opt_index)

	def on_add_one(self, code):
		self.d.GetValue('List_opt')
		self.d.GetValue('List_sel')
		if self.List_opt:
			item = self.List_opt[self.List_opt_index]
			self.List_sel.append(item)
			del self.List_opt[self.List_opt_index]
		self.d.PutValue('List_sel')
		self.d.PutValue('List_opt')
		self.checkLists()
			
	def on_add_all(self, code):
		self.d.GetValue('List_opt')
		self.d.GetValue('List_sel')
		if self.List_opt:
			self.List_sel += self.List_opt
			self.List_opt = []
		self.d.PutValue('List_sel')
		self.d.PutValue('List_opt')
		self.checkLists()

	def on_rem_one(self, code):
		self.d.GetValue('List_opt')
		self.d.GetValue('List_sel')
		if self.List_sel:
			self.List_opt.append(self.List_sel.pop(self.List_sel_index))
		self.d.PutValue('List_opt')
		self.d.PutValue('List_sel')
		self.checkLists()

	def on_rem_all(self, code):
		self.d.GetValue('List_opt')
		self.d.GetValue('List_sel')
		if self.List_sel:
			self.List_opt += self.List_sel
			self.List_sel = []
		self.d.PutValue('List_sel')
		self.d.PutValue('List_opt')
		self.checkLists()

	def on_move_up(self, code):
		self.d.GetValue('List_sel')
		myItem = self.List_sel.pop(self.List_sel_index)
		self.List_sel.insert(self.List_sel_index - 1, myItem)
		self.d.PutValue('List_sel')

	def on_move_dn(self, code):
		self.d.GetValue('List_sel')
		myItem = self.List_sel.pop(self.List_sel_index)
		self.List_sel.insert(self.List_sel_index + 1, myItem)
		self.d.PutValue('List_sel')

	def on_browse_file(self, code):
		self.d.GetValue('filename')
		file = fl.GetFileName(0, 'pdf', self.filename, '*.pdf')
		if file:
			self.filename = file
			self.d.PutValue('filename')

	def on_ok(self, code):
		if self.mode == 'normal':
			self.d.GetValue('List_sel')
			self.selection = self.List_sel

		elif self.mode == 'MM':
			self.d.GetValue('MMvalues')
			myMMvalues = string.replace(self.MMvalues, ' ', '')
			self.selection = myMMvalues.split(",")

			# Save instances into customdata of VFB
			if self.MMvalues != self.customdata['MMinstances']:
				self.MMfont.modified = 1
				fl.UpdateFont()
			self.customdata['MMinstances'] = self.MMvalues
			if self.MMfont.has_key('.notdef'):
				self.MMfont['.notdef'].customdata = writePlistToString(self.customdata)

		
		# Settings
#		preferences = Ddict(dict)
		#prefkeys = preferences['presets']['__default__'].keys()
		for pref in preferences['presets']['__default__'].keys():
			self.d.GetValue(pref)
			try:
				preferences['presets']['__default__'][pref] = eval('self.' + pref)
			except:
				pass
			preferences['presets']['__default__']['fontselection'] = self.List_sel
		
	def on_user_guide(self, code):
		launchfile(findFlsPath('Macros', 'Autopsy User Guide.pdf'))

	def Run(self):
		return self.d.Run()



def getFontByFullname(TheName):
	result = None
	for i in range(len(fl)):
		if fl[i].full_name == TheName:
			result = fl[i]
	return result


# Output to console
def output(text):
	if verbose:
		print "> " + str(text) + " <"




'''

TODO

- error message if full_name is empty.

- custom presets for GUI

for better handling of missing glyphs and zero-width glyphs:
- add a class for single graph values, that contain info about width and height of drawing space,
  and whether or not a point should be drawn there.

'''










"""plistlib.py -- a tool to generate and parse MacOSX .plist files.

The PropertList (.plist) file format is a simple XML pickle supporting
basic object types, like dictionaries, lists, numbers and strings.
Usually the top level object is a dictionary.

To write out a plist file, use the writePlist(rootObject, pathOrFile)
function. 'rootObject' is the top level object, 'pathOrFile' is a
filename or a (writable) file object.

To parse a plist from a file, use the readPlist(pathOrFile) function,
with a file name or a (readable) file object as the only argument. It
returns the top level object (again, usually a dictionary).

To work with plist data in strings, you can use readPlistFromString()
and writePlistToString().

Values can be strings, integers, floats, booleans, tuples, lists,
dictionaries, Data or datetime.datetime objects. String values (including
dictionary keys) may be unicode strings -- they will be written out as
UTF-8.

The <data> plist type is supported through the Data class. This is a
thin wrapper around a Python string.

Generate Plist example:

    pl = dict(
        aString="Doodah",
        aList=["A", "B", 12, 32.1, [1, 2, 3]],
        aFloat = 0.1,
        anInt = 728,
        aDict=dict(
            anotherString="<hello & hi there!>",
            aUnicodeValue=u'M\xe4ssig, Ma\xdf',
            aTrueValue=True,
            aFalseValue=False,
        ),
        someData = Data("<binary gunk>"),
        someMoreData = Data("<lots of binary gunk>" * 10),
        aDate = datetime.fromtimestamp(time.mktime(time.gmtime())),
    )
    # unicode keys are possible, but a little awkward to use:
    pl[u'\xc5benraa'] = "That was a unicode key."
    writePlist(pl, fileName)

Parse Plist example:

    pl = readPlist(pathOrFile)
    print pl["aKey"]
"""


__all__ = [
    "readPlist", "writePlist", "readPlistFromString", "writePlistToString",
    "readPlistFromResource", "writePlistToResource",
    "Plist", "Data", "Dict"
]
# Note: the Plist and Dict classes have been deprecated.

import binascii
from cStringIO import StringIO
import re
try:
    from datetime import datetime
except ImportError:
    # We're running on Python < 2.3, we don't support dates here,
    # yet we provide a stub class so type dispatching works.
    class datetime(object):
        def __init__(self, *args, **kwargs):
            raise ValueError("datetime is not supported")


def readPlist(pathOrFile):
    """Read a .plist file. 'pathOrFile' may either be a file name or a
    (readable) file object. Return the unpacked root object (which
    usually is a dictionary).
    """
    didOpen = 0
    if isinstance(pathOrFile, (str, unicode)):
        pathOrFile = open(pathOrFile)
        didOpen = 1
    p = PlistParser()
    rootObject = p.parse(pathOrFile)
    if didOpen:
        pathOrFile.close()
    return rootObject


def writePlist(rootObject, pathOrFile):
    """Write 'rootObject' to a .plist file. 'pathOrFile' may either be a
    file name or a (writable) file object.
    """
    didOpen = 0
    if isinstance(pathOrFile, (str, unicode)):
        pathOrFile = open(pathOrFile, "w")
        didOpen = 1
    writer = PlistWriter(pathOrFile)
    writer.writeln("<plist version=\"1.0\">")
    writer.writeValue(rootObject)
    writer.writeln("</plist>")
    if didOpen:
        pathOrFile.close()


def readPlistFromString(data):
    """Read a plist data from a string. Return the root object.
    """
    return readPlist(StringIO(data))


def writePlistToString(rootObject):
    """Return 'rootObject' as a plist-formatted string.
    """
    f = StringIO()
    writePlist(rootObject, f)
    return f.getvalue()


def readPlistFromResource(path, restype='plst', resid=0):
    """Read plst resource from the resource fork of path.
    """
    from Carbon.File import FSRef, FSGetResourceForkName
    from Carbon.Files import fsRdPerm
    from Carbon import Res
    fsRef = FSRef(path)
    resNum = Res.FSOpenResourceFile(fsRef, FSGetResourceForkName(), fsRdPerm)
    Res.UseResFile(resNum)
    plistData = Res.Get1Resource(restype, resid).data
    Res.CloseResFile(resNum)
    return readPlistFromString(plistData)


def writePlistToResource(rootObject, path, restype='plst', resid=0):
    """Write 'rootObject' as a plst resource to the resource fork of path.
    """
    from Carbon.File import FSRef, FSGetResourceForkName
    from Carbon.Files import fsRdWrPerm
    from Carbon import Res
    plistData = writePlistToString(rootObject)
    fsRef = FSRef(path)
    resNum = Res.FSOpenResourceFile(fsRef, FSGetResourceForkName(), fsRdWrPerm)
    Res.UseResFile(resNum)
    try:
        Res.Get1Resource(restype, resid).RemoveResource()
    except Res.Error:
        pass
    res = Res.Resource(plistData)
    res.AddResource(restype, resid, '')
    res.WriteResource()
    Res.CloseResFile(resNum)


class DumbXMLWriter:

    def __init__(self, file, indentLevel=0, indent="\t"):
        self.file = file
        self.stack = []
        self.indentLevel = indentLevel
        self.indent = indent

    def beginElement(self, element):
        self.stack.append(element)
        self.writeln("<%s>" % element)
        self.indentLevel += 1

    def endElement(self, element):
        assert self.indentLevel > 0
        assert self.stack.pop() == element
        self.indentLevel -= 1
        self.writeln("</%s>" % element)

    def simpleElement(self, element, value=None):
        if value is not None:
            value = _escapeAndEncode(value)
            self.writeln("<%s>%s</%s>" % (element, value, element))
        else:
            self.writeln("<%s/>" % element)

    def writeln(self, line):
        if line:
            self.file.write(self.indentLevel * self.indent + line + "\n")
        else:
            self.file.write("\n")


# Contents should conform to a subset of ISO 8601
# (in particular, YYYY '-' MM '-' DD 'T' HH ':' MM ':' SS 'Z'.  Smaller units may be omitted with
#  a loss of precision)
_dateParser = re.compile(r"(?P<year>\d\d\d\d)(?:-(?P<month>\d\d)(?:-(?P<day>\d\d)(?:T(?P<hour>\d\d)(?::(?P<minute>\d\d)(?::(?P<second>\d\d))?)?)?)?)?Z")

def _dateFromString(s):
    order = ('year', 'month', 'day', 'hour', 'minute', 'second')
    gd = _dateParser.match(s).groupdict()
    lst = []
    for key in order:
        val = gd[key]
        if val is None:
            break
        lst.append(int(val))
    return datetime(*lst)

def _dateToString(d):
    return '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
        d.year, d.month, d.day,
        d.hour, d.minute, d.second
    )


# Regex to find any control chars, except for \t \n and \r
_controlCharPat = re.compile(
    r"[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
    r"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f]")

def _escapeAndEncode(text):
    m = _controlCharPat.search(text)
    if m is not None:
        raise ValueError("strings can't contains control characters; "
                         "use plistlib.Data instead")
    text = text.replace("\r\n", "\n")       # convert DOS line endings
    text = text.replace("\r", "\n")         # convert Mac line endings
    text = text.replace("&", "&amp;")       # escape '&'
    text = text.replace("<", "&lt;")        # escape '<'
    text = text.replace(">", "&gt;")        # escape '>'
    return text.encode("utf-8")             # encode as UTF-8


PLISTHEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
"""

class PlistWriter(DumbXMLWriter):

    def __init__(self, file, indentLevel=0, indent="\t", writeHeader=1):
        if writeHeader:
            file.write(PLISTHEADER)
        DumbXMLWriter.__init__(self, file, indentLevel, indent)

    def writeValue(self, value):
        if isinstance(value, (str, unicode)):
            self.simpleElement("string", value)
        elif isinstance(value, bool):
            # must switch for bool before int, as bool is a
            # subclass of int...
            if value:
                self.simpleElement("true")
            else:
                self.simpleElement("false")
        elif isinstance(value, int):
            self.simpleElement("integer", str(value))
        elif isinstance(value, float):
            self.simpleElement("real", repr(value))
        elif isinstance(value, dict):
            self.writeDict(value)
        elif isinstance(value, Data):
            self.writeData(value)
        elif isinstance(value, datetime):
            self.simpleElement("date", _dateToString(value))
        elif isinstance(value, (tuple, list)):
            self.writeArray(value)
        else:
            raise TypeError("unsuported type: %s" % type(value))

    def writeData(self, data):
        self.beginElement("data")
        self.indentLevel -= 1
        maxlinelength = 76 - len(self.indent.replace("\t", " " * 8) *
                                 self.indentLevel)
        for line in data.asBase64(maxlinelength).split("\n"):
            if line:
                self.writeln(line)
        self.indentLevel += 1
        self.endElement("data")

    def writeDict(self, d):
        self.beginElement("dict")
        items = d.items()
        items.sort()
        for key, value in items:
            if not isinstance(key, (str, unicode)):
                raise TypeError("keys must be strings")
            self.simpleElement("key", key)
            self.writeValue(value)
        self.endElement("dict")

    def writeArray(self, array):
        self.beginElement("array")
        for value in array:
            self.writeValue(value)
        self.endElement("array")


class _InternalDict(dict):

    # This class is needed while Dict is scheduled for deprecation:
    # we only need to warn when a *user* instantiates Dict or when
    # the "attribute notation for dict keys" is used.

    def __getattr__(self, attr):
        try:
            value = self[attr]
        except KeyError:
            raise AttributeError, attr
        from warnings import warn
        warn("Attribute access from plist dicts is deprecated, use d[key] "
             "notation instead", PendingDeprecationWarning)
        return value

    def __setattr__(self, attr, value):
        from warnings import warn
        warn("Attribute access from plist dicts is deprecated, use d[key] "
             "notation instead", PendingDeprecationWarning)
        self[attr] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError, attr
        from warnings import warn
        warn("Attribute access from plist dicts is deprecated, use d[key] "
             "notation instead", PendingDeprecationWarning)

class Dict(_InternalDict):

    def __init__(self, **kwargs):
        from warnings import warn
        warn("The plistlib.Dict class is deprecated, use builtin dict instead",
             PendingDeprecationWarning)
        super(Dict, self).__init__(**kwargs)


class Plist(_InternalDict):

    """This class has been deprecated. Use readPlist() and writePlist()
    functions instead, together with regular dict objects.
    """

    def __init__(self, **kwargs):
        from warnings import warn
        warn("The Plist class is deprecated, use the readPlist() and "
             "writePlist() functions instead", PendingDeprecationWarning)
        super(Plist, self).__init__(**kwargs)

    def fromFile(cls, pathOrFile):
        """Deprecated. Use the readPlist() function instead."""
        rootObject = readPlist(pathOrFile)
        plist = cls()
        plist.update(rootObject)
        return plist
    fromFile = classmethod(fromFile)

    def write(self, pathOrFile):
        """Deprecated. Use the writePlist() function instead."""
        writePlist(self, pathOrFile)


def _encodeBase64(s, maxlinelength=76):
    # copied from base64.encodestring(), with added maxlinelength argument
    maxbinsize = (maxlinelength//4)*3
    pieces = []
    for i in range(0, len(s), maxbinsize):
        chunk = s[i : i + maxbinsize]
        pieces.append(binascii.b2a_base64(chunk))
    return "".join(pieces)

class Data:

    """Wrapper for binary data."""

    def __init__(self, data):
        self.data = data

    def fromBase64(cls, data):
        # base64.decodestring just calls binascii.a2b_base64;
        # it seems overkill to use both base64 and binascii.
        return cls(binascii.a2b_base64(data))
    fromBase64 = classmethod(fromBase64)

    def asBase64(self, maxlinelength=76):
        return _encodeBase64(self.data, maxlinelength)

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.data, other.data)
        elif isinstance(other, str):
            return cmp(self.data, other)
        else:
            return cmp(id(self), id(other))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.data))


class PlistParser:

    def __init__(self):
        self.stack = []
        self.currentKey = None
        self.root = None

    def parse(self, fileobj):
        from xml.parsers.expat import ParserCreate
        parser = ParserCreate()
        parser.StartElementHandler = self.handleBeginElement
        parser.EndElementHandler = self.handleEndElement
        parser.CharacterDataHandler = self.handleData
        parser.ParseFile(fileobj)
        return self.root

    def handleBeginElement(self, element, attrs):
        self.data = []
        handler = getattr(self, "begin_" + element, None)
        if handler is not None:
            handler(attrs)

    def handleEndElement(self, element):
        handler = getattr(self, "end_" + element, None)
        if handler is not None:
            handler()

    def handleData(self, data):
        self.data.append(data)

    def addObject(self, value):
        if self.currentKey is not None:
            self.stack[-1][self.currentKey] = value
            self.currentKey = None
        elif not self.stack:
            # this is the root object
            self.root = value
        else:
            self.stack[-1].append(value)

    def getData(self):
        data = "".join(self.data)
        try:
            data = data.encode("ascii")
        except UnicodeError:
            pass
        self.data = []
        return data

    # element handlers

    def begin_dict(self, attrs):
        d = _InternalDict()
        self.addObject(d)
        self.stack.append(d)
    def end_dict(self):
        self.stack.pop()

    def end_key(self):
        self.currentKey = self.getData()

    def begin_array(self, attrs):
        a = []
        self.addObject(a)
        self.stack.append(a)
    def end_array(self):
        self.stack.pop()

    def end_true(self):
        self.addObject(True)
    def end_false(self):
        self.addObject(False)
    def end_integer(self):
        self.addObject(int(self.getData()))
    def end_real(self):
        self.addObject(float(self.getData()))
    def end_string(self):
        self.addObject(self.getData())
    def end_data(self):
        self.addObject(Data.fromBase64(self.getData()))
    def end_date(self):
        self.addObject(_dateFromString(self.getData()))


# cruft to support booleans in Python <= 2.3
import sys
if sys.version_info[:2] < (2, 3):
    # Python 2.2 and earlier: no booleans
    # Python 2.2.x: booleans are ints
    class bool(int):
        """Imitation of the Python 2.3 bool object."""
        def __new__(cls, value):
            return int.__new__(cls, not not value)
        def __repr__(self):
            if self:
                return "True"
            else:
                return "False"
    True = bool(1)
    False = bool(0)






LoadSettings()
main()
SaveSettings()