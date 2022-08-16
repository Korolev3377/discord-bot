class GameOfLife:
	def __init__(self, size):
		self.field = self.Field(size=size)
			
	class Field:
		def __init__(self, size=25, loop=False):
			self.size = size
			self.cells = []
			self.cur_x = 0
			self.cur_y = 0
			for y in range(self.size):
				for x in range(self.size):
					self.cells.append(self.Cell(x, y))
		
		class Cell:
			def __init__(self, x, y, status=False, next_status=False):
				self.x = x
				self.y = y
				self.status = status
				self.next_status = next_status
			
			def is_me(self, cell):
				if self.x == cell.x and self.y == cell.y:
					return True
				else: return False
			
			@property
			def name(self):
				return str(self.x)+str(self.y)
			
			def is_neighbor(self, cell):
				if cell.x in (self.x-1, self.x, self.x+1,) and cell.y in (self.y-1, self.y, self.y+1,) and not self.is_me(cell):
					return True
				else: return False
		
		def has_neighbors(self):
			self.print_field()
			for cell in self.cells:
				neighbors = []
				for neighbor in self.cells:
					if cell.is_neighbor(neighbor):
						neighbors.append((str(neighbor.x)+str(neighbor.y)))
				print(f"\nCell {str(cell.x)+str(cell.y)} has neighbors: {neighbors}")

		def move_cursor(self, x=0, y=0):
			if self.cur_x + x in range(self.size) and self.cur_y + y in range(self.size):
				self.cur_x += x
				self.cur_y += y
			
		def update(self):
			for cell in self.cells:
				online = 0
				for neighbor in self.cells:
					if cell.is_neighbor(neighbor):
						if neighbor.status:
							online += 1
				if cell.status:
					if online in (2, 3,):
						cell.next_status = True
					else:
						cell.next_status = False
				else:
					if online in (3,):
						cell.next_status = True
					else:
						cell.next_status = False
			for cell in self.cells:
				cell.status = cell.next_status
		
		def flip_cell(self):
			for cell in self.cells:
				if cell.x == self.cur_x and cell.y == self.cur_y:
					cell.status = False if cell.status else True
		
		def print_field(self):
			field = []
			for cell in self.cells:
				if cell.status:
					field.append("█")
				else:
					field.append("░")
			
			field_list = []
			for i in [field[i:i+self.size] for i in range(len(field))[::self.size]]:
				field_list.append("".join(i))
			
			control = []
			control.append(["0"])
			for x in range(self.size):
				control[0].append("2" if self.cur_x == x else "1")
			control[0] = "".join(control[0])
			
			for y in range(self.size):
				control.append([])
				control[y+1].append("3" if self.cur_y == y else "1")
				control[y+1].extend("".join(field_list[y]))
				control[y+1] = "".join(control[y+1])
			
			return "\n".join(control)