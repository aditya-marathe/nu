"""\
A GUI for browsing the digital labbook - an alternative to the CLI.
"""

__all__ = ['BrowserApp']

from typing import Any
# from typing import override  # NOTE Only in Python 3.12.x!

import tkinter as tk
from tkinter import ttk

WINDOW_SIZE = 1_200, 550

colours = {
    'White': '#ffffff',
    'Blue': '#084f6a',
    'Grey': '#f1f1f1',
    'Hover Grey': '#dedede'
}

fonts = {
    'Title': ('CMU Concrete', 12, 'bold'),
    'Text': ('CMU Sans Serif', 10),
    'Symbol': ('Wingdings', 10)
}


class _AutoHideScrollbar(ttk.Scrollbar):
    """\
    [Internal] Tkinter Scrollbar - only appears when required.
    """
    # @override  # NOTE Only in Python 3.12.x!
    def set(self, first: float, last: float):
        """\
        Overrides the `set` method for this instance of `ttk.Scrollbar`.
        """
        if float(first) <= 0. and float(last) >= 1.:
            self.pack_forget()
        else:
            self.pack(fill=tk.Y, side=tk.RIGHT)

        ttk.Scrollbar.set(self, first, last)


class _CustomButton(tk.Button):
    """\
    [Internal] Button which changes colour when hovered.    
    """
    def __init__(
            self,
            *args,
            hover_bg: str | None = None,
            hover_fg: str | None = None,
            **kwargs
        ) -> None:
        """\
        Initialises CustomButton.

        Args
        ----        
        hover_bg: str | None
            Button background colour when hovered.

        hover_fg: str | None
            Button foreground (text) colour when hovered.

        *button_args, **button_kwargs
            Arguments for `tk.Button`.
        """
        super().__init__(*args, **kwargs)

        self._default_bg, self._default_fg = self["bg"], self["fg"]

        self.hover_bg = hover_bg if hover_bg is not None else self["bg"]
        self.hover_fg = hover_fg if hover_fg is not None else self["fg"]

        self.bind("<Enter>", self._on_hover_event)
        self.bind("<Leave>", self._on_leave_event)

        self._command = kwargs.get("command", lambda: 0)
        self.bind("<Button-1>", self._exec_command, add=True)

    def _on_hover_event(self, *_) -> None:
        """\
        Changes button colour when triggered by a hover event.
        """
        self["bg"] = self.hover_bg
        self["fg"] = self.hover_fg

    def _on_leave_event(self, *_) -> None:
        """\
        Changes button colour back to normal when triggered by a leave event.
        """
        self["bg"] = self._default_bg
        self["fg"] = self._default_fg

    def _exec_command(self, *_) -> str:
        """\
        Wraps the command to modify behaviour of `tk.Button` using some cheeky
        Tkinter backend magic.
        """
        if self['state'] == tk.NORMAL:
            self._command()
      
        self._on_hover_event()

        return "break"


class _ScrollableFrame(tk.Frame):
    """\
    [Internal] Tkinter Frame with a Scrollbar.
    """
    def __init__(self, *args, **kwargs) -> None:
        """\
        Initialises ScrollableFrame.
        """
        super().__init__(*args, **kwargs)

        # Canvas (required for scrollbar widget...)
        self._canvas = tk.Canvas(
            self,
            bg=kwargs.get('bg', None) or kwargs.get('background', None),
            bd=0,
            highlightthickness=0
        )
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Container
        self.container = tk.Frame(
            self._canvas,
            bg=kwargs.get('bg', None) or kwargs.get('background', None),
            bd=0,
            highlightthickness=0
        )
        _canvas_window = self._canvas.create_window(
            (0, 0),
            window=self.container,
            anchor=tk.NW
        )

        # Scrollbar
        self._scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._canvas.yview
        )
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self.container.bind(
            '<Configure>', 
            lambda event: self._canvas.configure(
                scrollregion=self._canvas.bbox(tk.ALL)
            )
        )
        self._canvas.bind(
            '<Configure>',
            lambda event: self._canvas.itemconfig(
                _canvas_window,
                width=event.width
            )
        )


class _ListItem(tk.Frame):
    """\
    [Internal] List items in the sidebar.
    """
    def __init__(self, *args, details: dict[str, Any], **kwargs) -> None:
        """\
        Creates a list item.
        """
        super().__init__(*args, **kwargs)

        self.details = details

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        self.cb_state = tk.IntVar(self, value=False)

        ttk.Checkbutton(
            self,
            variable=self.cb_state,
            takefocus=False
        ).grid(row=0, column=0, padx=(5, 0), sticky=tk.W)

        bttn_kwargs = {
            'relief': tk.FLAT,
            'bg': colours['Grey'],
            'hover_bg': colours['Blue'],
            'hover_fg': colours['White']
        }

        _CustomButton(
            self,
            text=details.get('Name', '[No Name]'),
            anchor=tk.W,
            font=fonts['Text'],
            **bttn_kwargs
        ).grid(row=0, column=1, sticky=tk.NSEW)
        _CustomButton(
            self,
            text='P',
            font=fonts['Symbol'],
            **bttn_kwargs
        ).grid(row=0, column=2, sticky=tk.NSEW)


class BrowserApp(tk.Tk):
    """\
    Labbook Browser - a GUI application to view trained models.
    """
    def __init__(self) -> None:
        """\
        Initialises Browser.
        """
        super().__init__()

        self.title('Labbook')

        x_pos = int(0.5 * (self.winfo_screenwidth() - WINDOW_SIZE[0]))
        y_pos = int(0.3 * (self.winfo_screenheight() - WINDOW_SIZE[1]))

        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}+{x_pos}+{y_pos}')

        self.state('zoomed')

        self.iconbitmap('labbook/lblogo.ico')

        # -------------------
        #   Window menu bar
        # -------------------

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Project menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Project', menu=file_menu)
        file_menu.add_command(label='Create')
        file_menu.add_command(label='Open')
        file_menu.add_separator()
        file_menu.add_command(label='Close')

        # ------------------
        #   Window content
        # ------------------

        self.paned_window = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=5,
            bg=colours['Grey'],
            bd = 0
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.paned_window, bg=colours['White'])
        self.paned_window.add(self.sidebar)

        # Sidebar - Title
        tk.Label(
            self.sidebar,
            text='MODELS',
            bg=colours['White'],
            font=fonts['Title']
        ).pack(padx=10, pady=(10, 0), fill=tk.X)

        # ttk.Separator(
        #     self.sidebar,
        #     orient=tk.HORIZONTAL
        # ).pack(padx=50, pady=10, fill=tk.X)

        # Sidebar - List
        scrollable_frame = _ScrollableFrame(self.sidebar, bg=colours['Grey'])
        scrollable_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.list_frame = scrollable_frame.container

        self.sb_cb_vars: list[tk.IntVar] = []
        self.sb_sel_counter = tk.StringVar(self, value='No Selection.')

        self._init_sidebar()

        # Sidebar - Actions
        actions_container = tk.Frame(self.sidebar, bg=colours['White'])
        actions_container.pack(padx=10, pady=(0, 10), fill=tk.X)

        actions_container.columnconfigure(0, weight=1)
        actions_container.columnconfigure(1, weight=0)
        actions_container.columnconfigure(2, weight=0)

        tk.Label(
            actions_container,
            textvariable=self.sb_sel_counter,
            font=fonts['Text'],
            bg=colours['White']
        ).grid(row=0, column=0, sticky=tk.W)

        bttn_kwargs = {
            'font': fonts['Text'],
            'bg': colours['Grey'],
            'hover_bg': colours['Blue'],
            'hover_fg': colours['White'],
            'relief': tk.FLAT
        }

        self.sb_compare_bttn = _CustomButton(
            actions_container,
            text='Compare',
            **bttn_kwargs
        )
        self.sb_compare_bttn.grid(row=0, column=1, padx=2)

        self.sb_del_bttn = _CustomButton(
            actions_container,
            text='Delete',
            **bttn_kwargs
        )
        self.sb_del_bttn.grid(row=0, column=2, padx=(2, 0))

        # Container
        self.container = _ScrollableFrame(
            self.paned_window,
            bg=colours['White']
        )
        self.paned_window.add(self.container)

    def _init_sidebar(self) -> None:
        """\
        Initialises sidebar contents.
        """
        self.sb_cb_vars = []  # Resets this list

        for i in range(40):
            item = _ListItem(
                self.list_frame,
                details={},
                bg=colours['Grey'],
                highlightthickness=5,
                highlightbackground=colours['White']
            )
            item.pack(fill=tk.X)

            item.cb_state.trace_add(
                mode='write',
                callback=self._sb_update_counter
            )
            self.sb_cb_vars.append(item.cb_state)

    def _sb_update_counter(self, *_) -> None:
        sel_num = sum(var.get() for var in self.sb_cb_vars)
        self.sb_sel_counter.set(
            value=(f'{sel_num} Selected.' if sel_num else 'No Selection.')
        )


if __name__ == '__main__':
    app = BrowserApp()
    app.mainloop()
