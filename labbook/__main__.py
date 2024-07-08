"""
Main program for labbook: either launch the GUI or the CLI. Try `labbook --help` 
for more information.
"""

__all__ = []

from typing import Any

import click

from labbook.browser import BrowserApp


@click.group(invoke_without_command=True)
@click.pass_context
def cli(context: Any) -> None:
    """\
    Labbook CLI.
    """
    if context.invoked_subcommand is None:
        click.echo('Hello World!')


@click.command(name='browser')
def browser() -> None:
    """\
    Launches the Labbook GUI `Browser` app.
    """
    app = BrowserApp()
    app.mainloop()


cli.add_command(browser)


if __name__ == '__main__':
    cli()
