
class ColorSetter(object):

	def __init__(self):
		self.avail = None
		self.order = []
		self.load()

	def getColor(self):
		if not self.order:
			self.reset()
		col = str(self.order.pop())
		print(col)
		return col, str(self.avail[col])

	def reset(self):
		self.order = list(self.avail.keys())

	def load(self):
		self.avail = {
		    "aqua": "#00ffff",
		    # "azure": "#f0ffff",
		    "beige": "#f5f5dc",
		    # "black": "#000000",
		    "blue": "#0000ff",
		    "brown": "#a52a2a",
		    #"cyan": "#00ffff",
		    # "darkblue": "#00008b",
		    "dark cyan": "#008b8b",
		    "dark grey": "#a9a9a9",
		    #"dark green": "#006400",
		    "dark khaki": "#bdb76b",
		    # "darkmagenta": "#8b008b",
		    "dark olive green": "#556b2f",
		    "dark orange": "#ff8c00",
		    # "dark orchid": "#9932cc",
		    "dark red": "#8b0000",
		    "dark salmon": "#e9967a",
		    "dark violet": "#9400d3",
		    # "fuchsia": "#ff00ff",
		    "gold": "#ffd700",
		    "green": "#008000",
		    "indigo": "#4b0082",
		    "khaki": "#f0e68c",
		    # "lightblue": "#add8e6",
		    # "lightcyan": "#e0ffff",
		    #"lightgreen": "#90ee90",
		    # "lightgrey": "#d3d3d3",
		    # "lightpink": "#ffb6c1",
		    # "lightyellow": "#ffffe0",
		    "lime": "#00ff00",
		    "magenta": "#ff00ff",
		    "maroon": "#800000",
		    "navy": "#000080",
		    "olive": "#808000",
		    "orange": "#ffa500",
		    "pink": "#ffc0cb",
		    "purple": "#800080",
		    # "violet": "#800080",
		    # "red": "#ff0000",
		    # "silver": "#c0c0c0",
		    # "white": "#ffffff",
		    "yellow": "#ffff00"
		}




	# frame will store all instances on it in a dictionary { instance: box }
	#
