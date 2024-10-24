import tkinter as tk


class ToolTip:
    def __init__(self, widget, text, bg_color="#222222", fg_color="#FFFFFF"):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.mostrar_tooltip_id = None
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.widget.bind("<Enter>", self.iniciar_conteo)
        self.widget.bind("<Leave>", self.cancelar_conteo)

    def iniciar_conteo(self, event=None):
        self.cancelar_conteo()
        self.mostrar_tooltip_id = self.widget.after(1250, self.mostrar_tooltip)

    def cancelar_conteo(self, event=None):
        if self.mostrar_tooltip_id:
            self.widget.after_cancel(self.mostrar_tooltip_id)
            self.mostrar_tooltip_id = None
        self.ocultar_tooltip()

    def mostrar_tooltip(self):
        if not self.tooltip:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            label = tk.Label(
                self.tooltip,
                text=self.text,
                justify="left",
                background=self.bg_color,
                foreground=self.fg_color,
                relief="flat",
                borderwidth=0,
                font=("SF Pro Display", 9),
                padx=7,
                pady=3,
            )
            label.pack()
            tooltip_width = label.winfo_reqwidth()
            tooltip_height = label.winfo_reqheight()
            x = x - tooltip_width // 2
            screen_width = self.widget.winfo_screenwidth()
            screen_height = self.widget.winfo_screenheight()
            if x + tooltip_width > screen_width:
                x = screen_width - tooltip_width
            if x < 0:
                x = 0
            if y + tooltip_height > screen_height:
                y = self.widget.winfo_rooty() - tooltip_height - 5
            self.tooltip.wm_geometry(f"+{x}+{y}")
            self.tooltip.lift()
            self.tooltip.update_idletasks()
            self.tooltip.configure(bg=self.bg_color)
            label.configure(bg=self.bg_color)

    def ocultar_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def actualizar_colores(self, bg_color, fg_color):
        self.bg_color = bg_color
        self.fg_color = fg_color
        if self.tooltip:
            self.ocultar_tooltip()
            self.mostrar_tooltip()
