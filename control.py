from sublime_plugin import WindowCommand

LEFT, TOP, RIGHT, BOTTOM = (0,1,2,3)


class MoveViewCommand(WindowCommand):
	def run(self, direction):
		cview = self.window.active_view()
		cgroup = self.active_group()
		layout = self.window.get_layout()

		ngroup = self.get_best_view(cgroup, layout, direction)
		self.window.set_view_index(cview, ngroup, 0)
		self.window.focus_view(cview)

	def get_best_view(self, cgroup, layout, direction):
		""" Gets the most natural group on the border perpendicular to the moving direction.

		By most natural I mean the group which have the largest intersection with the current
		group on the border perpendicular to the movement direction.
		"""
		cells = layout['cells']
		cl = len(cells)
		ccell = cells[cgroup]

		# TODO: Maybe we should filter down the fields 
		if direction == 'down':
			icells = ((cell[0], cell[2], i) for i in xrange(cl) if cells[i][TOP] >= ccell[BOTTOM] and cells[i] != ccell)
		elif direction == 'up':
			icells = ((cell[0], cell[2], i) for i in xrange(cl) if cells[i][BOTTOM] <= ccell[TOP] and cells[i] != ccell)
		elif direction == 'left':
			icells = ((cell[1], cell[3], i) for i in xrange(cl) if cells[i][RIGHT] <= ccell[LEFT] and cells[i] != ccell)
		else: # direction == 'right'
			icells = ((cell[1], cell[3], i) for i in xrange(cl) if cells[i][LEFT] >= ccell[RIGHT] and cells[i] != ccell)

		if direction in ['down', 'up']:
			stuff = layout['cols']
			crange = [stuff[ccell[0]], stuff[ccell[2]]]
		else:
			stuff = layout['rows']
			crange = [stuff[ccell[1]], stuff[ccell[3]]]

		return self.get_best_intersection(cgroup, crange, icells, stuff)

	def get_best_intersection(self, cindex, current, others, distribution):
		best_value = 0.0
		best_index = cindex
		clow, chigh = current

		for low, high, index in others:
			mlow, mhigh = max(clow, low), min(high, chigh)
			if mlow <= mhigh and distribution[mhigh] - distribution[mlow] > best_value:
				best_value = distribution[mhigh] - distribution[mlow]
				best_index = index

		return best_index


class CreatePaneCommand(WindowCommand):
	def run(self, direction):
		pass


class MergePaneCommand(WindowCommand):
	def run(self):
		pass

class MoveFocusCommand(WindowCommand):
	def run(self, direction):
		pass

