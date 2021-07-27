"""Calendar PDF generation"""

import os
from dataclasses import dataclass
import functools

from typing import Optional

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from . import grids


def _register_fonts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    font_folder = os.path.join(current_path, "fonts")

    for font_file in os.listdir(font_folder):
        font_name, extension = os.path.splitext(font_file)
        if (extension) == ".ttf":
            pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_folder, font_file)))


_register_fonts()


@dataclass
class ColorStyle:
    """This is it's own class so I can keep them around as presets"""

    header_text_color: colors.HexColor
    letter_color: colors.HexColor
    date_color: colors.HexColor
    label_color: colors.HexColor

    title_color: Optional[colors.HexColor] = None

    outline_color: Optional[colors.HexColor] = None
    grid_line_color: Optional[colors.HexColor] = None
    header_divider_color: Optional[colors.HexColor] = None

    header_background_color: Optional[colors.HexColor] = None
    frame_background_color: Optional[colors.HexColor] = None

    header_divider_width: int = 1
    outline_width: int = 1
    grid_line_width: int = 1

    title_font_size: Optional[int] = None  # None or 0 is auto-sized

    header_font_name: str = "HelveticaNeue-Bold"
    letter_font_name: str = "HelveticaNeue-Light"
    date_font_name: str = "HelveticaNeue-Light"
    title_font_name: str = "HelveticaNeue-Bold"


@dataclass
class SizeStyle:
    """Preset for a PDF size"""

    width: float
    height: float
    top_margin: float
    bottom_margin: float
    left_margin: float
    right_margin: float

    @property
    def inner_height(self) -> float:
        """Calculate the inner height of the PDF"""

        return self.height - self.top_margin - self.bottom_margin

    @property
    def inner_width(self) -> float:
        """Calculate the inner width of the PDF"""

        return self.width - self.left_margin - self.right_margin


@dataclass
class CalendarGenerator:
    """A calendar generator draws a calendar on a canvas"""

    canvas: canvas.Canvas
    grid: grids.CalendarGrid

    colors: ColorStyle

    left_offset: float
    bottom_offset: float
    width: float
    height: float

    # Used to track how much vertical space we've used
    _used_top_space: float = 0

    def draw(self):
        """Execute the actual draw"""

        self._draw_title()
        self._draw_frame()
        self._draw_header()
        self._draw_grid()
        self._draw_dates()
        self._draw_letters()

    def _draw_title(self):
        if not self.colors.title_color:
            return

        font_size = self._get_title_font_size()
        ascent, descent = pdfmetrics.getAscentDescent(self.colors.title_font_name, font_size)

        y_pos = (self.bottom_offset + self.height) - (ascent+descent)

        self.canvas.setFont(self.colors.title_font_name, font_size)
        self.canvas.setFillColor(self.colors.title_color)

        # This is outside the frame, so we're going to use the left offset directly
        self.canvas.drawString(self.left_offset, y_pos, self.grid.title)
        self._used_top_space += font_size  # Bump down with the 20% pad

    def _draw_frame(self):
        if not (self.colors.frame_background_color or (self.colors.outline_width and self.colors.outline_color)):
            return

        draw_stroke = 0
        draw_fill = 0

        x_pos = self.left_offset
        y_pos = self.bottom_offset

        width = self.width
        height = self.height - self._used_top_space

        # Draw the bounding box
        if self.colors.outline_width and self.colors.outline_color:
            draw_stroke = 1

            # We have to do this manually instead of with the internal calculators
            # because we are the one that modifies it,
            # and we are trying to draw on the line
            x_pos += self.colors.outline_width/2
            y_pos += self.colors.outline_width/2

            width = width - self.colors.outline_width
            height = height - self.colors.outline_width

            self.canvas.setLineWidth(self.colors.outline_width)
            self.canvas.setStrokeColor(self.colors.outline_color)

        if self.colors.frame_background_color:
            draw_fill = 1

            self.canvas.setFillColor(self.colors.frame_background_color)

        self.canvas.rect(x_pos, y_pos, width, height, stroke=draw_stroke, fill=draw_fill)

    def _draw_header(self):
        header_font_size = self._get_header_font_size()
        header_height = header_font_size * 1.5
        header_width = self._internal_width / len(self.grid.headers)

        # Draw the header background
        if self.colors.header_background_color:
            x_pos = self._x_position
            y_pos = self._get_element_y_pos_from_top(header_height)

            self.canvas.setFillColor(self.colors.header_background_color)
            self.canvas.rect(x_pos, y_pos, self._internal_width, header_height, stroke=0, fill=1)

        # Draw the text elements
        self.canvas.setFillColor(self.colors.header_text_color)
        self.canvas.setFont(self.colors.header_font_name, header_font_size)

        for i, header in enumerate(self.grid.headers):
            x_pos = self._x_position + header_width/2 + header_width * i

            # Default padding is 120%, so .1 is half of the padding margin
            y_pos = self._get_element_y_pos_from_top(header_font_size) - header_height*.1

            self.canvas.drawCentredString(x_pos, y_pos, header)

        # Draw the lines between each header
        if self.colors.header_divider_color:
            self.canvas.setStrokeColor(self.colors.header_divider_color)
            bottom = self._get_element_y_pos_from_top(header_height)
            top = self._get_element_y_pos_from_top()

            self.canvas.setLineWidth(self.colors.header_divider_width)

            for i in range(len(self.grid.headers)):
                # Don't draw a line on the left page border
                if i == 0:
                    continue

                x_pos = self._x_position + i*header_width - self.colors.header_divider_width/2
                self.canvas.line(x_pos, bottom, x_pos, top)

        self._used_top_space += header_height

    def _draw_grid(self):
        if not self.colors.grid_line_color and not self.colors.grid_line_width:
            return

        self.canvas.setLineWidth(self.colors.grid_line_width)
        self.canvas.setStrokeColor(self.colors.grid_line_color)

        for column_index in range(1, len(self.grid.headers)):
            x_pos = self._x_position + self._column_width * column_index - self.colors.grid_line_width/2
            top = self._get_element_y_pos_from_top()
            bottom = self._get_element_y_pos_from_top(self._internal_remaining_height)

            self.canvas.line(x_pos, top, x_pos, bottom)

        row_height = self._internal_remaining_height / self._row_count

        for row_index in range(len(self.grid.grid)):
            left = self._x_position
            right = self._x_position + self._internal_width

            y_pos = self._get_element_y_pos_from_top(row_height * row_index)

            self.canvas.line(left, y_pos, right, y_pos)

    def _draw_letters(self):
        if not self.colors.letter_color:
            return

        font_size = self._get_letter_font_size()
        row_height = self._internal_remaining_height / self._row_count

        _, descent = pdfmetrics.getAscentDescent(self.colors.letter_font_name, font_size)

        for row_index, row in enumerate(self.grid.grid):
            y_pos = self._get_element_y_pos_from_top(font_size + row_height*row_index) - descent/2

            for col_index, col in enumerate(row):
                if not col or not col.letter:
                    continue

                if col.is_label:
                    label_font_size = get_font_size_maximum_width(col.letter,
                                                                  self._column_width*.9,
                                                                  self.colors.letter_font_name)

                    _, label_descent = pdfmetrics.getAscentDescent(self.colors.letter_font_name, label_font_size)

                    label_y_pos = self._get_element_y_pos_from_top(label_font_size) \
                        - (row_height * (row_index + 1)) \
                        + label_font_size - label_descent

                    x_pos = self._x_position + (col_index)*self._column_width + self._column_width/2

                    self.canvas.setFont(self.colors.letter_font_name, label_font_size)
                    self.canvas.setFillColor(self.colors.label_color)
                    self.canvas.drawCentredString(x_pos, label_y_pos, col.letter)

                else:
                    self.canvas.setFont(self.colors.letter_font_name, font_size)
                    self.canvas.setFillColor(self.colors.letter_color)
                    # We have to get the right bound here, thus the +1, and pad it out, thus the - 5%
                    x_pos = self._x_position + (col_index)*self._column_width + self._column_width * 0.05
                    self.canvas.drawString(x_pos, y_pos, col.letter)

    def _draw_dates(self):
        if not self.colors.date_color:
            return

        font_size = self._get_date_font_size()
        row_height = self._internal_remaining_height / self._row_count
        self.canvas.setFillColor(self.colors.date_color)
        self.canvas.setFont(self.colors.date_font_name, font_size)

        _, descent = pdfmetrics.getAscentDescent(self.colors.date_font_name, font_size)

        for row_index, row in enumerate(self.grid.grid):
            y_pos = self._get_element_y_pos_from_top(font_size + row_height*row_index) - descent

            for col_index, col in enumerate(row):
                if not col or not col.date:
                    continue

                # We have to get the right bound here, thus the +1, and pad it out, thus the - 5%
                x_pos = self._x_position + (col_index+1)*self._column_width - self._column_width * 0.05
                self.canvas.drawRightString(x_pos, y_pos, str(col.date.day))

    @property
    def _column_width(self) -> float:
        """Determine the width of each column"""

        return float(self._internal_width) / len(self.grid.headers)

    @property
    def _x_position(self) -> float:
        """The X position that we can start drawing at, given frames and such"""

        if self.colors.outline_width and self.colors.outline_color:

            # Don't divide by 2 because we're pushing the line so it's fully enclosed within the width
            return self.left_offset + self.colors.outline_width

        return self.left_offset

    @property
    def _internal_width(self) -> float:
        """The internally accessible width, given frames and such"""

        if self.colors.outline_width and self.colors.outline_color:
            # The line is pushed fully within the bounding box, so take both sides of it into account

            return self.width - self.colors.outline_width*2

        return self.width

    @property
    def _internal_remaining_height(self) -> float:
        out = self.height

        if self.colors.outline_color and self.colors.outline_width:
            out -= self.colors.outline_width*2

        out -= self._used_top_space

        return out

    @property
    def _row_count(self):

        # We have a minimum of 5 rows in a calendar - 4 looks weird
        return max(len(self.grid.grid), 5)

    def _get_element_y_pos_from_top(self, element_height: float = 0) -> float:
        """Get the Y position to draw a bottom referenced element, given a height"""

        out = self.bottom_offset + self.height - element_height - self._used_top_space

        if self.colors.outline_width and self.colors.outline_color:
            out -= self.colors.outline_width

        return out

    def _get_title_font_size(self) -> float:
        if self.colors.title_font_size:
            return self.colors.title_font_size

        max_size = self.width * .5
        return get_font_size_maximum_width(self.grid.title, max_size, self.colors.title_font_name)

    def _get_header_font_size(self) -> float:
        maximum_width = self._column_width * .8

        if self.colors.header_divider_width and self.colors.header_divider_color:
            maximum_width -= self.colors.header_divider_width

        current_size = self._column_width  # Set an upper bound to keep the column header at most squarish

        for header in self.grid.headers:
            possible_size = get_font_size_maximum_width(header, maximum_width, self.colors.header_font_name)
            if possible_size < current_size:
                current_size = possible_size

        return current_size

    def _get_date_font_size(self) -> float:
        all_dates = set()

        for row in self.grid.grid:
            for col in row:
                if col and col.date:
                    all_dates.add(str(col.date.day))

        # Calculate how big we can be, up to 50% of the height of the cell
        letter_font_size = self._get_letter_font_size()

        all_letters = set()
        for row in self.grid.grid:
            for col in row:
                if col and col.letter and not col.is_label:
                    all_letters.add(col.letter)

        letter_widths = (stringWidth(letter, self.colors.letter_font_name, letter_font_size) for letter in all_letters)
        max_letter_width = max(*letter_widths)

        # Allow up to the lesser of half the cell, or 60% of the remaining space
        space_available = min((self._column_width - max_letter_width)*.6, self._column_width / 2)
        max_day_widths = (get_font_size_maximum_width(day, space_available, self.colors.date_font_name)
                          for day in all_dates if day)

        theoretical_max = min(*max_day_widths)

        # Allow either the width-based max from above, or half the cell height
        return min(theoretical_max, (self.height / self._row_count) * .5)

    @functools.cache
    def _get_letter_font_size(self) -> float:
        all_letters = set()

        for row in self.grid.grid:
            for col in row:
                if col and col.letter and not col.is_label:
                    all_letters.add(col.letter)

        # Letters get 80% of the cell
        maximum_width = self._column_width * .8

        if self.colors.grid_line_color and self.colors.grid_line_width:
            maximum_width -= self.colors.grid_line_width

        row_height = self._internal_remaining_height / self._row_count

        # Maximum of 80% of the row height, if we have a really weirdly shaped calendar here
        current_size = row_height
        for letter in all_letters:
            possible_size = get_font_size_maximum_width(letter, maximum_width, self.colors.date_font_name)

            if possible_size < current_size:
                current_size = possible_size

        return current_size


def get_font_size_maximum_width(text: str, maximum: float, font: str) -> float:
    """Get the maximum font size to fit some given text into a given width"""

    font_size = 12
    width = stringWidth(text, font, font_size)
    return maximum/width * font_size
