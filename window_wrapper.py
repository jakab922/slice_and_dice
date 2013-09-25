import sublime

LEFT, TOP, RIGHT, BOTTOM = (0, 1, 2, 3)
direction_translator = {
    'left': LEFT,
    'up': TOP,
    'right': RIGHT,
    'down': BOTTOM
}
HORIZONTAL, VERTICAL = 0, 1


class InvalidOperation(Exception):
    pass


class Cell(object):
    def __init__(self, cell):
        for direction in ("left", "up", "right", "down"):
            ndirection = direction_translator[direction]
            setattr(self, direction, cell[ndirection])


class Window(object):
    def __init__(self, sublime_window):
        self.sublime_window = sublime_window
        self.config = sublime.load_settings('slice_and_dice.sublime-settings')

    @property
    def _layout(self):
        layout = self.sublime_window.get_layout()
        return layout["cells"], layout["rows"], layout["cols"]

    @property
    def _aview(self):
        return self.sublime_window.active_view()

    @property
    def _agroup(self):
        return self.sublime_window.active_group()

    def cut_cell(self, cut_direction):
        # Cut cell with either a horizontal or a vertical line
        pass

    def merge_cell(self, direction):
        # If there is a cell in the given direction where the opposite side is
        # the same size as the size perpendicular to the direction than we
        # merge, otherwise we don't.
        pass

    def move_view_to_cell(self, cell_index, view):
        # move the view from one cell to another and focus on the view
        pass

    def move_focus(self, direction):
        # Get the best group in the given direction and if there is any
        # focus on that group
        pass

    def shrink_cell(self, cell_index, direction, percentage):
        pass

    def grow_cell(self, cell_index, direction, percentage):
        pass

    def _set_layout(self, cells, rows, cols, normalize=True):
        if normalize:
            cells, rows, cols = self._normalize_layout(cells, rows, cols)
        layout = {
            "cells": cells,
            "rows": rows,
            "cols": cols
        }
        self.sublime_window.set_layout(layout)

    def _normalize_layout(self, cells, rows, cols):
        rlen = len(rows)
        r_eps = 1.0 / (rlen - 1)
        rows = [0.0] + [r_eps * i for i in xrange(1, rlen)] + [1.0]

        clen = len(cols)
        c_eps = 1.0 / (len(cols) - 1)
        cols = [0.0] + [c_eps * i for i in xrange(1, clen)] + [1.0]

        return cells, rows, cols

    def _get_best_group(self, cell_index):
        pass
