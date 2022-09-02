from __future__ import annotations

import pandas as pd
from lib.utils import dunders
from secrets import choice
from typing import List, Dict


colours = ['magenta', 'green', 'blue', 'yellow', 'red', 'orange', 'violet', 'white']

exclude_colours = {'yellow': 'orange',
                'magenta': 'violet',
                'green': 'yellow',
                'blue': 'magenta'}

y_dict = {'Adj_Close': 'Actual_Values',
        'Predicted_Values': 'Predicted_Values'}

class line_plotter(dunders):
    """Plotter class that plots lines for Dash line plots.
    """

    def __init__(self, df: pd.DataFrame,  x_name: str, all_y: dict) -> None:
        self.df = df
        self.x_name = x_name
        self.all_y = all_y
        super().__init__()

    @staticmethod
    def _plot_lines(df: pd.DataFrame, x: str, y: str, line_colour: str, name: str) -> dict:
        """Dictionary template for lines of Dash plot.

        Args:
            * `df` (pd.DataFrame): DataFrame containing the data. 
            * `x` (str): `x-axis` name for pd.DataFrame.loc property to access.
            * `y` (str): `y-axis` name for pd.DataFrame.loc property to access.
            * `line_colour` (str): Colour of the line to plot.
            * `name` (str): Name of the line in legend.

        Returns:
            dict: Dictionary containing all the line information for Dash.
        """

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
    def _reject_sample(lst: list, exception: str) -> str:   # Used to exclude orange when yellow is picked (vice/versa).
        """Reject a random list sample based on exception and return 
        a new random sample from the list.

        Args:
            * `lst` (list): List to pick element from.
            * `exception` (str): Element to exclude.

        Returns:
            `str`: New random sample excluding the exception.
        """

        while True:
            picked = choice(lst)
            if picked != exception:
                return picked

    def colour_exclusion(self, current_colour: str, dictionary: dict, exclusion_lst: list) -> str:
        """Exlusion algorithm to exclude colours that can create clutter on the graph. 

        Args:
            * `current_colour` (str): Current colour instance.
            * `dictionary` (dict): Colour exclusion pairs.
            * `exclusion_lst` (list): Colours that were previously picked. 

        Returns:
            `str`: New colour sample that is not an exclusion pair.
        """

        if len(exclusion_lst) == 0:     # Only when the first dictionary containing the plot line information is generated.
            return 0

        for key, value in dictionary.items():   # Only after the first dictionary containing the plot line information is generated.
            if key == current_colour:
                continue 
            if value == current_colour:
                continue

            for i in exclusion_lst:
                if i == key:
                    result = self._reject_sample(lst = colours, exception = value)
                elif i == value:
                    result = self._reject_sample(lst = colours, exception = key)
                else:
                    result = 0
                    continue
        return result

    def plot_generator(self) -> List[Dict[str, str]]:
        """Dictionary generator containing plot information for Dash.

        Returns:
            `List[Dict[str, str]]`: List of dictionaries were each dictionary is a line in the Dash plot.
        """

        out_list = []
        colour_checks = []
        for key, value in self.all_y.items():
            colour = choice(colours)
            if len(colour_checks) == 0:
                colour_checks.append(colour)

            check_bad_colours = self.colour_exclusion(current_colour = colour,
                                                    dictionary = exclude_colours,
                                                    exclusion_lst = colour_checks)

            if not check_bad_colours == 0:
                colour = check_bad_colours

            out_dict = self._plot_lines(df = self.df, x = self.x_name, y = key,
                            line_colour = colour, name = value)
            out_list.append(out_dict)
        return out_list