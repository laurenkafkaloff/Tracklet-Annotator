class ColorSetter(object):

	def __init__(self):
		self.avail = None
		self.order = []
		self.load()

	def getColor(self):
		if not self.order:
			self.reset()
		col = str(self.order.pop())
		return col, str(self.avail[col])

	def reset(self):
		self.order = ['forest green', 'light pink', 'maroon', 'brown', 'beige', 'teal', 'magenta', 'bright pink', 'dark purple', 'dark blue',
					  'royal blue', 'bright blue', 'bright green', 'bright yellow', 'dark orange', 'bright red', 'pink', 'purple', 'blue',
					  'light blue', 'green', 'lime', 'yellow', 'orange', 'red']

	def load(self):
		# self.avail = {
		#     "aqua": "#00ffff",
		#     "beige": "#f5f5dc",
		#     "blue": "#0000ff",
		#     "brown": "#a52a2a",
		#     "cyan": "#008b8b",
		#     "grey": "#a9a9a9",
		#     "khaki": "#bdb76b",
		#     "olive green": "#556b2f",
		#     "dark orange": "#ff8c00",
		#     "red": "#8b0000",
		#     "salmon": "#e9967a",
		#     "violet": "#9400d3",
		#     "gold": "#ffd700",
		#     "green": "#008000",
		#     "indigo": "#4b0082",
		#     "khaki": "#f0e68c",
		#     "lime": "#00ff00",
		#     "magenta": "#ff00ff",
		#     "maroon": "#800000",
		#     "navy": "#000080",
		#     "olive": "#808000",
		#     "orange": "#ffa500",
		#     "pink": "#ffc0cb",
		#     "purple": "#800080",
		#     "yellow": "#ffff00"
		# }
		self.avail = {
		    "red": "#FF7878",
		    "orange": "#FFCC99",
		    "yellow": "#FFFF99",
		    "lime": "#CCFF99",
		    "green": "#77FF88",
		    "light blue": "#33FFFF",
		    "blue": "#99CCFF",
		    "purple": "#CC99FF",
		    "pink": "#FF99FF",
		    "bright red": "#FF3333",
		    "dark orange": "#FF8000",
		    "bright yellow": "#FFFF00",
		    "bright green": "#00FF00",
		    "bright blue": "#00FFFF",
		    "royal blue": "#0080FF",
		    "dark blue": "#0000FF",
		    "dark purple": "#7F00FF",
		    "bright pink": "#FF00FF",
		    "magenta": "#FF007F",
		    "teal": "#009999",
		    "beige": "#FFE5CC",
		    "brown": "#994C00",
		    "maroon": "#990000",
		    "light pink": "#FFCCE5",
		    "forest green": "#00994C"
		}
