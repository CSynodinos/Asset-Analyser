import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

np.set_printoptions(formatter={'float_kind':'{:f}'.format})

class _df_ops(ABC):

    @abstractmethod
    def _row_subtract(self):
        pass

    @abstractmethod
    def _get_col_numpy(self, idx):
        pass

    @abstractmethod
    def _actual_pred_numpy(self):
        pass

    @abstractmethod
    def _percent_diff(self):
        pass

class df_analyses(_df_ops):
    def __init__(self, df:pd.DataFrame) -> None:
        self.df = df

    def _get_col_numpy(self, idx) -> np.ndarray:
        return self.df.iloc[:, idx].to_numpy()

    def _actual_pred_numpy(self):
        return self._get_col_numpy(idx = 2), self._get_col_numpy(idx = 1)

    def _row_subtract(self) -> np.ndarray:
        return np.subtract(self._actual_pred_numpy()[0], self._actual_pred_numpy()[1])

    def _percent_diff(self) -> np.ndarray:
        pred, actual = self._actual_pred_numpy()
        difference = ((np.subtract(pred, actual)) * 100)
        return np.true_divide(difference, actual)

    def assessment_df_parser(self):
        result_diff = self._row_subtract()
        self.df['Difference'] = result_diff.tolist()
        self.df['Percent_Difference'] =  self._percent_diff().tolist()
        return self.df