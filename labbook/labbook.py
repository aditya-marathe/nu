"""\
Module contains the `Labbook` class used to manage machine learning projects.
"""
__all__ = ['Labbook']

from typing import Any

import pathlib
from datetime import datetime
from pydantic import BaseModel
from pydantic import field_validator
import json

import joblib

DATE_FMT = '%d-%m-%Y %H:%M'


def _process_dir(path: str | pathlib.Path) -> pathlib.Path:
    """\
    Converts a string path to a `pathlib.Path` object and checks if it exists.

    Parameters
    ----------
    path : str | pathlib.Path
        The target path to check.

    Returns
    -------
    pathlib.Path
        The target path as a `pathlib.Path` object.

    Raises
    ------
    FileNotFoundError
        If the target path does not exist.
    """
    if isinstance(path, str):
        path = pathlib.Path(path)

    if not path.exists():
        raise FileNotFoundError(f'No such file or directory: \'{path}\'')

    return path


class _Model(BaseModel):
    """\
    [Internal] Model dataclass - used to store model information.
    """
    Name: str
    Time: datetime
    Comments: str
    TrainedOn: list[str]
    XVars: list[str]
    YVars: list[str]
    Transforms: list[str]
    Pickled: dict[str, Any]
    Flagged: bool = False

    @field_validator('Time', mode='before')
    def parse_time(cls, value: str) -> datetime:
        return datetime.strptime(value, DATE_FMT)


class _Project(BaseModel):
    Name: str
    Comments: dict[str, str]  # Stores the time in key and comment in value
    Models: list[_Model]
    # Dir: pathlib.Path


def _new_project(name: str, project: pathlib.Path) -> _Project:
    ...


def _open_project(project_path: pathlib.Path) -> _Project:
    """\
    Opens are reads a saved project.

    Parameters
    ----------
    project_path : pathlib.Path
        The path to the project.

    Returns
    -------
    _Project
        The project as a Pydantic `_Project` object.
    """
    with open(file=project_path / 'labbook.json', mode='r') as file:
        data = json.load(file)

    return _Project(**data)


class Labbook:
    """\
    Manages a machine learning project.

    Notes
    -----
        This version of `Labbook` is compatible with: TensorFlow, and Sci-Kit 
        Learn projects.
    """

    def __init__(self, project_path: str | pathlib.Path) -> None:
        """\
        Initialise a `Labbook` object and open a project.
        """
        self._project_path = _process_dir(path=project_path)
        self._project = _open_project(project_path=self._project_path)

    # @classmethod
    # def create_new_project(
    #     cls,
    #     project_name: str,
    #     project_dir: str | pathlib.Path
    # ) -> Labbook:
    #     ...

    def __str__(self) -> str:
        return (
            f'[Labbook] Loaded \'{self._project.Name}\' project with '
            f'{len(self._project.Models)} trained model(s).'
        )

    def __repr__(self) -> str:
        return str(self)

    # def _repr_html_(self) -> str:  # TODO Would be nice to have.
    #     return ''
