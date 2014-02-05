from sublime_plugin import WindowCommand
import sublime

LEFT, TOP, RIGHT, BOTTOM = (0, 1, 2, 3)
SLICE, CREATE = (0, 1)


class BaseCommand(WindowCommand):
    direction_translator = {
        'left': LEFT,
        'up': TOP,
        'right': RIGHT,
        'down': BOTTOM
    }

    type_translator = {
        "slice": SLICE,
        "create": CREATE
    }

    def _load_settings(self):
        self.settings = sublime.load_settings('slice_and_dice.'
                                              'sublime-settings')

    def _extract_layout(self):
        layout = self.window.get_layout()
        self.cells = layout["cells"]
        self.rows = layout["rows"]
        self.cols = layout["cols"]

    def run(self, direction=None):
        if direction is not None:
            self.direction = self.direction_translator[direction]
        self._load_settings()
        self.type = self.settings.get("type")
        self._extract_layout()
        self.current_group = self.window.active_group()
        self.current_view = self.window.active_view()

    def set_layout(self):
        layout = {
            "rows": self.rows,
            "cols": self.cols,
            "cells": self.cells
        }
        self.window.set_layout(layout)

    def normalize_rows(self):
        self.rows[0] = 0.0
        total = len(self.rows) - 1
        value = 1.0 / total
        for i in xrange(total - 1):
            self.rows[i + 1] = (i + 1) * value
        self.rows[-1] = 1.0

    def normalize_cols(self):
        self.cols[0] = 0.0
        self.cols[-1] = 1.0
        total = len(self.cols) - 1
        value = 1.0 / total
        for i in xrange(total - 1):
            self.cols[i + 1] = (i + 1) * value

# TODO: Replace successive subset of columns/rows where
#       the set of cells in the neighboring columns are the same.
#       This is an important normalization step since when we remove
#       cells we want to remove unneeded row/col cuts too.


class ToggleTypeCommand(BaseCommand):
    def run(self, *args, **kwargs):
        self._load_settings()
        if self.settings.get("type") == "slice":
            self.settings.set("type", "create")
        else:
            self.settings.set("type", "slice")
        sublime.save_settings('slice_and_dice.sublime-settings')


class CreateColumnCommand(BaseCommand):
    def run(self):
        super(CreateColumnCommand, self).run()
        border = self.cells[self.current_group][RIGHT]
        for cell in self.cells:
            if cell[LEFT] >= border:
                cell[LEFT] += 1
            if cell[RIGHT] > border:
                cell[RIGHT] += 1

        self.cols = self.cols[:(border + 1)] + [0] + self.cols[(border + 1):]
        self.cells.append([border, 0, border + 1, len(self.rows) - 1])
        self.normalize_cols()
        self.set_layout()


class CreateRowCommand(BaseCommand):
    def run(self):
        super(CreateRowCommand, self).run()
        border = self.cells[self.current_group][BOTTOM]
        for cell in self.cells:
            if cell[TOP] >= border:
                cell[TOP] += 1
            if cell[BOTTOM] > border:
                cell[BOTTOM] += 1

        self.rows = self.rows[:(border + 1)] + [0] + self.rows[(border + 1):]
        self.cells.append([0, border, len(self.cols) - 1, border + 1])
        self.normalize_rows()
        self.set_layout()


class BaseMoveCommand(BaseCommand):
    cell_move_values = [
        (TOP, BOTTOM, RIGHT, LEFT),
        (LEFT, RIGHT, BOTTOM, TOP),
        (TOP, BOTTOM, LEFT, RIGHT),
        (LEFT, RIGHT, TOP, BOTTOM)
    ]

    def run(self, direction):
        super(BaseMoveCommand, self).run(direction)

    def get_best_intersection(self, current_range, icells, distribution):
        """ Finds the group which has the largest border with the active
            group perpendicular to self.direction.

        :param current_range: The indexes marking the beginning and the end of
                              the current cell in the row/col array depending
                              on direction.
        :param icells: Generator of triples where the first 2 are border
                       indexes and the last is the cells index in
                       the cell array.
        :param distribution: The col/row cut array depending on the direction.

        :rtype: The index of the group which has the largest border
                with the current group.
        """
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

    def get_best_group(self):
        """ Gets the most natural group on the border perpendicular to the
            moving direction.

        By most natural I mean the group which has the largest intersection
        with the current group on the border perpendicular to the movement
        direction.
        """
        cells = self.cells
        current_cell = cells[self.current_group]

        first, second, other, this = self.cell_move_values[self.direction]
        icells = ((cell[first], cell[second], i) for i, cell in enumerate(cells)
                  if cell[other] == current_cell[this] and cell != current_cell)

        if self.direction in [TOP, BOTTOM]:
            distribution = self.cols
            current_range = (current_cell[LEFT], current_cell[RIGHT])
        else:
            distribution = self.rows
            current_range = (current_cell[TOP], current_cell[BOTTOM])

        return self.get_best_intersection(current_range, icells, distribution)


class MoveFocusCommand(BaseMoveCommand):
    def run(self, direction):
        super(MoveFocusCommand, self).run(direction)

        next_group = self.get_best_group()
        if next_group != self.current_group:
            self.window.focus_group(next_group)


class MoveViewCommand(BaseMoveCommand):
    def run(self, direction):
        super(MoveViewCommand, self).run(direction)

        next_group = self.get_best_group()
        if next_group != self.current_group:
            self.window.set_view_index(self.current_view, next_group, 0)
            self.window.focus_view(self.current_view)


# TODO: close_command needs the successive step renormalization step.
class CloseCellCommand(BaseCommand):
    opposites = [RIGHT, BOTTOM, LEFT, TOP]

    def run(self):
        super(CloseCellCommand, self).run()

        direction, cell_indexes = self.get_cover()
        print "direction: %s" % direction
        print "cell_indexes: %s" % cell_indexes

        if direction is not None:
            opposite = self.opposites[direction]

            new_value = self.cells[self.current_group][opposite]
            print "new_value: %s" % new_value
            print "opposite: %s" % opposite
            for index in cell_indexes:
                self.cells[index][opposite] = new_value

            print "self.cells: %s" % self.cells
            print "self.current_group: %s" % self.current_group
            cg = self.current_group
            self.cells = self.cells[:cg] + self.cells[cg + 1:]
            print "self.cells: %s" % self.cells
            # This should be a function START
            candidate = cell_indexes[0]
            other_index = (candidate if candidate < self.current_group else
                           candidate - 1)
            views = self.window.views_in_group(self.current_group)
            other_count = len(self.window.views_in_group(other_index))
            for i, view in enumerate(views):
                self.window.set_view_index(view, other_index, other_count + i)
            if views:
                self.window.focus_view(views[0])
            # This should be a function END
            self.set_layout()
        else:
            sublime.status_message("Cell can't be merged to "
                                   "any neighboring cells")
            """Can happen(cell in the middle):

                 -------- --
                |        |  |
                 --------|  |
                |  |     |  |
                |  |     |  |
                |  |----- --
                |  |        |
                |  |        |
                 -- --------

            """

    def get_cover(self):
        current_cell = self.cells[self.current_group]

        covers = [
            {
                "min": max(current_cell[BOTTOM], current_cell[RIGHT]),
                "max": min(current_cell[TOP], current_cell[LEFT]),
                "cell_indexes": []
            } for _ in xrange(4)
        ]
        mimas = [(1, 3), (0, 2), (1, 3), (0, 2)]

        for i in xrange(len(self.cells)):
            if i == self.current_group:
                continue
            checked_cell = self.cells[i]
            for direction in (LEFT, TOP, RIGHT, BOTTOM):
                if direction == RIGHT:
                    print "current_cell: %s" % current_cell
                    print "checked_cell: %s" % checked_cell
                    print "RIGHT: %s" % RIGHT
                    print "self.opposites[RIGHT]: %s" % self.opposites[RIGHT]
                if current_cell[direction] == \
                   checked_cell[self.opposites[direction]]:

                    low, high = mimas[direction][0], mimas[direction][1]
                    if checked_cell[low] >= current_cell[low] and \
                       checked_cell[high] <= current_cell[high]:

                        covers[direction]["min"] = min(covers[direction]["min"],
                                                       checked_cell[low])
                        covers[direction]["max"] = max(covers[direction]["max"],
                                                       checked_cell[high])
                        covers[direction]["cell_indexes"].append(i)
                    break

        print "covers: %s" % covers

        for i, cover in enumerate(covers):
            low, high = mimas[i][0], mimas[i][1]
            current_range = current_cell[high] - current_cell[low]
            cover_range = sum([self.cells[index][high] - self.cells[index][low]
                               for index in cover["cell_indexes"]])
            if cover["min"] == current_cell[low] and \
               cover["max"] == current_cell[high] and \
               current_range == cover_range:
                return i, cover["cell_indexes"]

        return None, None
