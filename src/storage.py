"""where API stores uploaded datasets and stores as requests continue"""

import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    """class for dataset and metadata after dataset is uploaded"""

    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        """stores copy of data and returns new integer ID"""
        self._counter += 1
        dataset_id = self._counter
        self._store[dataset_id] = {"filename": filename, "df": df.copy()}
        logger.debug("stored dataset: id=%d, rows=%d", dataset_id, len(df))
        return dataset_id

    def get(self, dataset_id):
        """returns copy of dataframe, or none if not in set"""
        entry = self._store.get(dataset_id)
        if entry is None:
            return None
        df = entry["df"].copy()
        logger.debug("retrieved dataset copy: id=%d, rows=%d", dataset_id, len(df))
        return df

    def get_metadata(self, dataset_id):
        """returns dataset metadata(i.e. id, filename, rows, columns, etc)"""
        entry = self._store.get(dataset_id)
        if entry is None:
            return None
        df = entry["df"]
        return {
            "id": dataset_id,
            "filename": entry["filename"],
            "rows": len(df),
            "columns": df.shape[1],
            "column_names": [str(col) for col in df.columns],
        }

    def update(self, dataset_id, df):
        """replaces existing dataset; returns true, or false if missing"""
        if dataset_id not in self._store:
            return False
        self._store[dataset_id]["df"] = df.copy()
        logger.debug("Updated dataset: id=%d, rows=%d", dataset_id, len(df))
        return True

    def clear(self):
        """clears all data and resets id counter"""
        self._store.clear()
        self._counter = 0
