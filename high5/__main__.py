"""
Main program for high5: either launch the GUI in default mode or directly open
a HDF5 file. Try `high5 --help` for more information.
"""

__all__ = []

import click

from high5.gui import H5Inspect


@click.command()
@click.option(
    '--file-path', '-F',
    type=click.Path(exists=True),
    help='The path to the HDF5 (*.h5) file to inspect.'
)
# @click.argument()
def main(file_path: str | None = None) -> None:
    """\
    Either launch the GUI in default mode or directly open a HDF5 file. 

    Parameters
    ----------
    file_path : str | None
        The path to the HDF5 (*.h5) file to inspect. Defaults to `None`.
    """
    if file_path:
        app = H5Inspect(file_path=file_path)
    else:
        app = H5Inspect()

    app.mainloop()


if __name__ == '__main__':
    main()
