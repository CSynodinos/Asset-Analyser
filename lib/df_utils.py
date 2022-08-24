#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from lib.utils import dunders

np.set_printoptions(formatter = {'float_kind':'{:f}'.format})   # Format numpy array results as floats

class _df_ops(ABC):
    """Abstact class for all the dataframe methods. Inherited by the df_analyses class.
    """

    @abstractmethod
    def _row_subtract(self) -> np.ndarray:
        """Subtract two numpy arrays.

        Returns:
            `np.ndarray`: Numpy array with the results from the subtraction 
            of every element from the initial arrays.
        """
        pass

    @abstractmethod
    def _get_col_numpy(self, idx: int) -> np.ndarray:
        """Get a all column values via column index. 

        Args:
            * `idx` (int): Column index number.

        Returns:
            `np.ndarray`: Column values in an ordered numpy array.
        """
        pass

    @abstractmethod
    def _actual_pred_numpy(self) -> tuple[np.ndarray, np.ndarray]:
        """Get actual and predicted values from numpy arrays.

        Returns:
            `tuple[np.ndarray, np.ndarray]`: An array for the actual values and another array
            for the predicted values.
        """
        pass

    @abstractmethod
    def _percent_diff(self) -> np.ndarray:
        """Get the percent difference between elements of two numpy arrays.

        Returns:
            `np.ndarray`: A numpy array containg the percent differences.
        """
        pass

    @abstractmethod
    def assessment_df_parser(self) -> pd.DataFrame:
        """Parser of all array calculations.

        Returns:
            `pd.DataFrame`: Dataframe containing all the initial database values
            plus two extra columns: Difference and Percent_Difference.
        """
        pass

    @abstractmethod
    def lst_assess(self, lst: list, threshold: float | int) -> list:
        """Assess list for above threshold elements.

        Args:
            * `lst` (list): List to loop through.
            * `threshold` (float | int): Threshold defined by user (both int and float supported).

        Returns:
            `list`: Holds above threshold values only.
        """
        pass

class df_analyses(_df_ops, dunders):
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super().__init__()

    def _get_col_numpy(self, idx: int) -> np.ndarray:
        return self.df.iloc[:, idx].to_numpy()

    def _actual_pred_numpy(self) -> tuple[np.ndarray, np.ndarray]:
        return self._get_col_numpy(idx = 2), self._get_col_numpy(idx = 1)

    def _row_subtract(self) -> np.ndarray:
        return np.subtract(self._actual_pred_numpy()[0], self._actual_pred_numpy()[1])

    def _percent_diff(self) -> np.ndarray:
        pred, actual = self._actual_pred_numpy()
        difference = ((np.subtract(pred, actual)) * 100)
        return np.true_divide(difference, actual)

    def assessment_df_parser(self) -> pd.DataFrame:
        result_diff = self._row_subtract()
        self.df['Difference'] = result_diff.tolist()
        self.df['Percent_Difference'] =  self._percent_diff().tolist()
        return self.df

    @staticmethod
    def lst_assess(lst: list, threshold: float | int) -> list:
        if not (isinstance(threshold, int) or isinstance(threshold, float)):
            raise TypeError(f'Threshold parameter can only be a float or int, not {type(threshold).__name__}')
        above = []
        for i in lst:
            i = float(i)
            if i >= threshold and i != None:
                above = above.append(i)
        return above