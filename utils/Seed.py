from typing import Set, Union, Optional

from utils.Coverage import Location
from utils.ObjectUtils import dump_object, load_object, get_md5_of_object
import os


class Seed:
    """Represent an input with additional attributes"""

    def __init__(self, data: Optional[str] = None, coverage: Optional[Set[Location]] = None,
                 id: Optional[str] = None, directory: str = './seedDB') -> None:
        """Initialize from seed data"""
        # self.data = data

        # These will be needed for advanced power schedules
        # self.coverage: Set[Location] = _coverage
        self.energy = 0.0
        self._data_cache: Optional[str] = None
        self._coverage_cache: Optional[Set[Location]] = None

        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

        if data is not None:
            self.id = get_md5_of_object(data)
            self._data_cache = data
            if coverage is not None:
                self._coverage_cache = coverage
            else:
                self._coverage_cache = set()
            self.save()
        elif id is not None:
            self.id = id
        else:
            raise ValueError("Either `data` or `id` must be provided.")

    @property
    def data_path(self) -> str:
        return os.path.join(self.directory, f'{self.id}.data')

    @property
    def coverage_path(self) -> str:
        return os.path.join(self.directory, f'{self.id}.cov')

    def __str__(self) -> str:
        """Returns data as string representation of the seed"""
        # return self.data
        try:
            return self.load_data()
        except:
            return ""

    __repr__ = __str__

    def save(self):
        if self._data_cache is not None:
            with open(self.data_path, 'w') as f:
                f.write(self._data_cache)

        if self._coverage_cache is not None:
            dump_object(self.coverage_path, self._coverage_cache)

    def load_data(self) -> str:
        if self._data_cache is None:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Seed data not found: {self.data_path}")
            with open(self.data_path, 'r') as f:
                self._data_cache = f.read()
        return self._data_cache

    def load_coverage(self) -> Set[Location]:
        if self._coverage_cache is None:
            if not os.path.exists(self.coverage_path):
                raise FileNotFoundError(f"Seed coverage not found: {self.coverage_path}")
            self._coverage_cache = load_object(self.coverage_path)
        return self._coverage_cache
