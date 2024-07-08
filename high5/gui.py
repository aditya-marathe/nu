"""\
Inspect the structure of a HDF5 database.
"""

__all__ = ['H5Inspect']

import warnings

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import h5py


warnings.filterwarnings('ignore', category=RuntimeWarning)


OPEN_TITLE = 'high5 | {}'
WINDOW_SIZE = 690, 600

# Style Settings
FONT = ('CMU Sans Serif', 10)
HEADING_FONT = ('CMU Concrete', 9, 'bold')
OFFWHITE = '#F1F4F2'


class H5Inspect(tk.Tk):
    """\
    A GUI for inspecting HDF5 databases.
    """

    def __init__(self, file_path: str | None = None) -> None:
        """\
        Initialises `H5Inspect`.
        """
        super().__init__()

        self.title('high5')

        x_pos = int(0.5 * (self.winfo_screenwidth() - WINDOW_SIZE[0]))
        y_pos = int(0.2 * (self.winfo_screenheight() - WINDOW_SIZE[1]))

        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}+{x_pos}+{y_pos}')

        self.resizable(False, False)

        # Style Stuff

        self.config(bg=OFFWHITE)

        self.style = ttk.Style()
        self.style.configure(
            '.',
            font=FONT,
        )
        self.style.configure(
            'Treeview',
            font=FONT,
            rowheight=22,
            indent=15,
            bd=0
        )
        self.style.configure(
            'Treeview.Heading',
            font=HEADING_FONT,
            bg=OFFWHITE
        )

        self.style.layout(
            'Treeview',
            [('Treeview.treearea', {'sticky': tk.NSEW})]
        )

        # Content

        self.open_button = ttk.Button(
            self,
            text='Open',
            takefocus=False,
            command=self.on_open_button_press
        )
        self.open_button.pack(expand=True)

        # NOTE This is last because it is the slowest to load...
        self.iconbitmap('./high5/h5.ico')

        # If called from CLI
        if file_path:
            self.on_open_button_press(file_path=file_path)

    def on_open_button_press(self, *_, file_path: str | None = None) -> None:
        """\
        Open an HDF5 file.
        """
        # Open a tkinter file dialog to select an HDF5 file
        file_path = file_path or filedialog.askopenfilename(
            parent=self,
            filetypes=[('HDF5', '*.h5')],
            initialdir='./',
            title='Open a HDF5 File'
        )

        if not file_path:  # If method is called from button press
            return

        self.config(cursor='watch')
        self.open_button.pack_forget()

        self.update()

        # Treeview Widget
        columns = [
            ('NAME', 320, tk.W),
            ('MIN', 80, tk.CENTER),
            ('MAX', 80, tk.CENTER),
            ('MEAN', 80, tk.CENTER),
            ('LENGTH', 95, tk.CENTER)
        ]

        tree = ttk.Treeview(
            self,
            columns=[f'#{i}' for i in range(len(columns) + 1)]
        )
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        # Treeview Widget - Columns
        for i, col in enumerate(tree['columns']):
            if not i:
                tree.column(column=col, width=20, minwidth=20, stretch=False)
                continue

            tree.heading(
                column=col, text=columns[i - 1][0], anchor=columns[i - 1][2]
            )
            tree.column(
                column=col,
                width=columns[i - 1][1],
                minwidth=columns[i - 1][1],
                stretch=False,
                anchor=columns[i - 1][2]
            )

        # Treeview Widget - Content
        with h5py.File(file_path, 'r') as file:

            for key, branch in file.items():
                tree.insert(
                    parent='',
                    index='end',
                    iid=key,
                    values=(
                        key,
                        '-',
                        '-',
                        '-',
                        len(branch.keys())
                    )
                )

                for child_key, data in branch.items():
                    data = data[:]

                    if data.shape[1] == 1:
                        shape = f'{data.shape[0]:,}'
                    else:
                        shape = f'{data.shape[0]:,}x{data.shape[1]:,}'

                    data = data.flatten()

                    tree.insert(
                        parent=key,
                        index='end',
                        iid=f'{key}.{child_key}',
                        values=(
                            f'{key}.{child_key}',
                            f'{data.min():0.3E}',
                            f'{data.max():0.3E}',
                            f'{data.mean():0.3E}',
                            shape
                        )
                    )

        file_name = file_path.split('/')[-1]
        self.title(OPEN_TITLE.format(file_name))

        self.config(cursor='')


if __name__ == '__main__':
    app = H5Inspect()
    app.mainloop()
