class ScreenLogger:
    def __init__(self, colours, bg_colour=None, max_value=None, min_value=None):
        """__init__

        :param list colours: a list of colours to use for data lines

        :param int bg_colour: a background colour to use (default black)

        :param int max_value: the max value to show on the plotter (the top)

        :param int min_value: the min value to show on the plotter (the bottom)
        """
        import displayio
        from pimoroni_envirowing import screen

        self.display = screen.Screen()

        self.num_colours = len(colours) + 1

        self.bitmap = displayio.Bitmap(160, 80, self.num_colours)

        self.palette = displayio.Palette(self.num_colours)

        if bg_colour:
            self.palette[0] = bg_colour
        else:
            self.palette[0] = 0x000000 # black

        for i,j in enumerate(colours):
            self.palette[i+1] = j
        
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)

        self.group = displayio.Group(max_size=12)

        self.group.append(self.tile_grid)

        self.display.show(self.group)

        if max_value:
            self.max_value = max_value
        else:
            self.max_value = 2**16 - 1 # max 16 bit value (unsigned)

        if min_value:
            self.min_value = min_value
        else:
            self.min_value = 0 # min 16 bit value (unsigned)
        
        self.value_range = self.max_value - self.min_value

        self.data_points = []

    def remap(self, Value, OldMin,OldMax, NewMin, NewMax):
        return (((Value - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    
    def update(self, *values):
        """update

        :param *values: the values to send to the logger
        """
        
        values = list(values)

        if len(values) > (self.num_colours - 1):
            raise Exception("The list of values shouldn't have more entries than the list of colours")
        
        for i,j in enumerate(values):
            if j > self.max_value:
                values[i] = self.max_value
            if j < self.min_value:
                values[i] = self.min_value

        """
        #TODO: Scroll the screen here
        for i in range(1, (self.bitmap.width*self.bitmap.height)):
            if (i + 1) % self.bitmap.width != 0:
                self.bitmap[i] = self.bitmap[i+1]
            else:
                self.bitmap[i] = 0

        for index,value in enumerate(values):
            self.bitmap[(self.bitmap.width - 1),round(((value - self.min_value) / self.value_range) * self.bitmap.height)] = index + 1
        """

        old_points = self.data_points

        self.data_points.append(values)

        if len(self.data_points) > self.bitmap.width:
            self.data_points = self.data_points[1:] # pop doesn't work in circuitpython
        
            difference = []

            for i,j in zip(self.data_points, old_points):
                subarray = []
                for value in zip(i,j):
                    subarray.append((value[0] - value[1]))
                difference.append(subarray)

            for index,value in enumerate(difference):
                for subindex,point in enumerate(value):
                    if point != 0:
                        #self.bitmap[index,round(((old_points[index][subindex] - self.min_value) / self.value_range) * -(self.bitmap.height -1) + (self.bitmap.height -1))] = 0
                        self.bitmap[index,round(self.remap(old_points[index][subindex], self.min_value, self.max_value, self.bitmap.height - 1, 0))] = 0
                        #self.bitmap[index,round(((self.data_points[index][subindex] - self.min_value) / self.value_range) * -(self.bitmap.height -1) + (self.bitmap.height -1))] = subindex + 1
                        self.bitmap[index,round(self.remap(self.data_points[index][subindex], self.min_value, self.max_value, self.bitmap.height - 1, 0))] = subindex + 1
        else:
            
            for subindex,point in enumerate(self.data_points[-1]):
                #self.bitmap[(len(self.data_points) - 1),round(((point - self.min_value) / self.value_range) * -(self.bitmap.height -1) + (self.bitmap.height -1))] = subindex + 1
                self.bitmap[(len(self.data_points) - 1),round(self.remap(point, self.min_value, self.max_value, self.bitmap.height - 1, 0))] = subindex + 1