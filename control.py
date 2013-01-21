from sublime_plugin import WindowCommand


LEFT, TOP, RIGHT, BOTTOM = (0,1,2,3)

dir_trans = {
	'left': LEFT,
	'up': TOP,
	'right': RIGHT,
	'down': BOTTOM
}

cell_values = [
	(1, 3, RIGHT, LEFT),
	(0, 2, BOTTOM, TOP),
	(1, 3, LEFT, RIGHT),
	(0, 2, TOP, BOTTOM)
]


"""
One can get the window layout with calling get_layout
on a sublime.Window object.

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

	def run(self, direction)


class MoveViewCommand(WindowCommand):
	def run(self, direction):
		# TODO: raise some bad direction error if direction not in dir_trans
		cview = self.window.active_view()
		cgroup = self.active_group()
		layout = self.window.get_layout()

		ngroup = self.get_best_group(cgroup, layout, dir_trans[direction])
		self.window.set_view_index(cview, ngroup, 0)
		self.window.focus_view(cview)

	def get_best_group(self, cgroup, layout, direction):
		""" Gets the most natural group on the border perpendicular to the moving direction.

		By most natural I mean the group which have the largest intersection with the current
		group on the border perpendicular to the movement direction.
		"""
		cells = layout['cells']
		cl = len(cells)
		ccell = cells[cgroup]

		first, second, other, this = cell_values[direction]
		icells = ((cell[first], cell[second], i) for i in xrange(cl) if cells[i][other] == ccell[this] and cells[i] != ccell)

		if direction in [TOP, BOTTOM]:
			stuff = layout['cols']
			crange = [stuff[ccell[0]], stuff[ccell[2]]]
		else:
			stuff = layout['rows']
			crange = [stuff[ccell[1]], stuff[ccell[3]]]

		return self.get_best_intersection(cgroup, crange, icells, stuff)

	def get_best_intersection(self, cindex, current, others, distribution):
		# TODO: Move this function out of the class since it's used by other calsses as well
		# 			or create a baseclass and subclass that for all commands.

		best_value = 0.0
		best_index = cindex
		clow, chigh = current

		for low, high, index in others:
			mlow, mhigh = max(clow, low), min(high, chigh)
			if mlow <= mhigh and distribution[mhigh] - distribution[mlow] > best_value:
				best_value = distribution[mhigh] - distribution[mlow]
				best_index = index

		return best_index


class CreateViewCommand(WindowCommand):
	def run(self, direction):
		pass


class MergeViewCommand(WindowCommand):
	def run(self, direction):
		pass

class MoveFocusCommand(WindowCommand):
	def run(self, direction):
		pass

