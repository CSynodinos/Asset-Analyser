from __future__ import annotations

import pandas as pd
from lib.utils import dunders
from secrets import choice


colours = ['magenta', 'green', 'blue', 'yellow', 'red', 'orange', 'violet']

y_dict = {'Adj_Close': 'Actual_Values',
        'Predicted_Values': 'Predicted_Values'}

class line_plotter(dunders):
    def __init__(self, df: pd.DataFrame,  x_name: str, all_y: dict) -> None:
        self.df = df
        self.x_name = x_name
        self.all_y = all_y
        super().__init__()

    @staticmethod
    def _plot_lines(df: pd.DataFrame, x: str, y: str, line_colour: str, name: str) -> dict:
        return {
        "x": df.loc[:, x],
        "y": df.loc[:, y],
        "type": "lines",
        "line": dict(color = line_colour),
        "name": name,
        "hovertemplate": "$%{y:.2f}"
                        "<extra></extra>",
        }

    @staticmethod
    def reject_sample(lst: list, exception: str) -> str:
        while True:
            picked = choice(lst)
            if picked != exception:
                return picked

    def plot_generator(self):
        out_list = []
        colour_checks = []
        for key, value in self.all_y.items():
            colour = choice(colours)
            if len(colour_checks) == 0:
                colour_checks.append(colour)
            colour_match = 'yellow'
            if colour_match in colour_checks:
                colour = self.reject_sample(lst = colours, exception = 'orange')

            out_dict = self._plot_lines(df = self.df, x = self.x_name, y = key,
                            line_colour = colour, name = value)
            out_list.append(out_dict)
        return out_list