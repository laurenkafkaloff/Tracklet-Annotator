class ColorSetter(object):

    def __init__(self):
        self.colorToId = {
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
        self.idToColor = {
            "#FF7878": "red",
            "#FFCC99": "orange",
            "#FFFF99": "yellow",
            "#CCFF99": "lime",
            "#77FF88": "green",
            "#33FFFF": "light blue",
            "#99CCFF": "blue",
            "#CC99FF": "purple",
            "#FF99FF": "pink",
            "#FF3333": "bright red",
            "#FF8000": "dark orange",
            "#FFFF00": "bright yellow",
            "#00FF00": "bright green",
            "#00FFFF": "bright blue",
            "#0080FF": "royal blue",
            "#0000FF": "dark blue",
            "#7F00FF": "dark purple",
            "#FF00FF": "bright pink",
            "#FF007F": "magenta",
            "#009999": "teal",
            "#FFE5CC": "beige",
            "#994C00": "brown",
            "#990000": "maroon",
            "#FFCCE5": "light pink",
            "#00994C": "forest green"
        }
        self.order = []

    def getColor(self):
        if not self.order:
            self.reset()
        col = self.colorToId[self.order.pop()]
        return col

    def reset(self):
        self.order = ['forest green', 'light pink', 'maroon', 'brown', 'beige', 'teal', 'magenta', 'bright pink', 'dark purple', 'dark blue',
                      'royal blue', 'bright blue', 'bright green', 'bright yellow', 'dark orange', 'bright red', 'pink', 'purple', 'blue',
                      'light blue', 'green', 'lime', 'yellow', 'orange', 'red']
