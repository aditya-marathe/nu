"""\
Labbook package for managing machine learning experiments.

Package features the `Labbook` class for saving and loading trained machine 
learning models. Currently supports TensorFlow and Sci-Kit Learn projects. 

Includes a GUI and CLI interface for checking or comparing saved models.

Developed by Aditya Marathe, 2024. This package is under the GNU General Public 
License version 3 - see 'LISCENSE' for details.

Notes
-----
    Future plans: add support to PyTorch models and create a `Scheduler` for 
    training and saving several models using a user provided scheme. 
"""

__all__ = ['Labbook']

__version__ = '0.0.1'

from labbook.labbook import Labbook
