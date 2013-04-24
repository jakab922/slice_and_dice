from sublime_plugin import WindowCommand
import sublime


LEFT, TOP, RIGHT, BOTTOM = (0,1,2,3)

direction_translator = {
	'left': LEFT,
	'up': TOP,
	'right': RIGHT,
	'down': BOTTOM
}

cell_move_values = [
	(TOP, BOTTOM, RIGHT, LEFT),
	(LEFT, RIGHT, BOTTOM, TOP),
	(TOP, BOTTOM, LEFT, RIGHT),
	(LEFT, RIGHT, TOP, BOTTOM)
]

cell_cut_values = [(LEFT, RIGHT), (TOP, BOTTOM), (LEFT, RIGHT), (TOP, BOTTOM)]

eps = 0.001

"""
One can get the window layout with calling get_layout
on a sublime.Window object.

The positive direction for x axis is right and for the y it's down

The return value is a dictionary with 3 keys:

- rows: A list of floats in [0,1] which defines where the
				row the row cuts in the view are. More on cuts in
				the description of cells.
- cols: Same as rows just for columns..
- cells: A list of 4 element list each of which define a cell.
				 The 4 elements are pointers to the cut arrays and they
				 define the cell geometry by [start_x, start_y, end_x, end_y]
				 pointer order.
"""

# TODO: Create a stack which can store view changing commands, so we can go back an forth in the view change history.


class BaseViewCommand(WindowCommand):

	def run(self, direction):
		self.current_view = self.window.active_view()
		self.current_group = self.window.active_group()
		self.layout = self.window.get_layout()
		self.direction = direction_translator[direction]

	def get_best_intersection(self, current_range, icells, distribution):
		best_value = 0.0
		best_index = self.current_group
		current_low, current_high = current_range

		for cell_low, cell_high, index in icells:
			intersection_low = max(current_low, cell_low)
			intersection_high = min(cell_high, current_high)
			intersection_value = distribution[intersection_high]
			intersection_value -= distribution[intersection_low]

			if intersection_value > best_value:
				best_value = intersection_value
				best_index = index

		return best_index


class MoveViewCommand(BaseViewCommand):
	def run(self, direction):
		super(MoveViewCommand, self).run(direction)

		next_group = self.get_best_group()
		if next_group != self.current_group:
			self.window.set_view_index(self.current_view, next_group, 0)
			self.window.focus_view(self.current_view)

	def get_best_group(self):
		""" Gets the most natural group on the border perpendicular to the moving direction.

		By most natural I mean the group which have the largest intersection with the current
		group on the border perpendicular to the movement direction.
		"""
		cells = self.layout['cells']
		current_cell = cells[self.current_group]

		first, second, other, this = cell_move_values[self.direction]
		icells = ((cell[first], cell[second], i) for i, cell in enumerate(cells)
				  if cell[other] == current_cell[this] and cell != current_cell)

		if self.direction in [TOP, BOTTOM]:
			distribution = self.layout['cols']
			current_range = (current_cell[LEFT], current_cell[RIGHT])
		else:
			distribution = self.layout['rows']
			current_range = (current_cell[TOP], current_cell[BOTTOM])

		return self.get_best_intersection(current_range, icells, distribution)


class CreateViewCommand(BaseViewCommand):
	def run(self, direction):
		super(CreateViewCommand, self).run(direction)
		print "create_view got called with direction: %s" % direction

		cells = self.layout['cells']
		current_cell = cells[self.current_group]

		if self.direction in [TOP, BOTTOM]:
			distribution = self.layout['rows']
			distro_type = 'rows'
			low_index, high_index = current_cell[TOP], current_cell[BOTTOM]
		else:
			distribution = self.layout['cols']
			distro_type = 'cols'
			low_index, high_index = current_cell[LEFT], current_cell[RIGHT]

		new_value = (distribution[high_index] - distribution[low_index]) / 2.0
		need_new_value = True
		middle_index = None

		for index, element in enumerate(distribution):
			if abs(element - new_value) < eps:
				need_new_value = False
				new_value = element
				middle_index = index
				break
			elif element > new_value:
				middle_index = index
				break
		print "middle_index: %s" % middle_index

		if need_new_value:
			distribution = distribution[:middle_index] + [new_value] + distribution[middle_index:]
			cell_indexes = cell_cut_values[self.direction]
			for cell in cells:
				for cell_index in cell_indexes:
					if cell[cell_index] >= middle_index:
						cell[cell_index] += 1

		old_cell = [el for el in current_cell]
		new_cell = [el for el in current_cell]
		low_modify, high_modify = cell_cut_values[self.direction]
		if self.direction in (TOP, LEFT):
			old_cell[low_modify] = middle_index
			new_cell[high_modify] = middle_index
		else:
			print "should be here"
			old_cell[high_modify] = middle_index
			new_cell[low_modify] = middle_index
		cells[self.current_group] = old_cell
		cells.append(new_cell)

		if distro_type == 'cols':
			layout_dict = {
				'cols': distribution,
				'rows': self.layout['rows'],
				'cells': cells
			}
		else:
			layout_dict = {
				'cols': self.layout['cols'],
				'rows': distribution,
				'cells': cells
			}

		print "layout_dict: %s" % layout_dict

		self.window.set_layout(layout_dict)


class KillViewCommand(BaseViewCommand):
	def run(self, direction):
		pass

# class MergeViewCommand(BaseViewCommand):
# 	def run(self, direction):
# 		pass

class MoveFocusCommand(BaseViewCommand):
	def run(self, direction):
		pass

class ViewHistoryCommand(BaseViewCommand):
	def run(self, direction):
		pass


