import customtkinter as ctk

class SearchBox(ctk.CTkFrame):
    def __init__(self, master, valores, placeholder="Pesquisar...", width=200, ao_selecionar=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.valores = valores
        self.ao_selecionar = ao_selecionar
        self.width = width
        self._construir(placeholder)

    def _construir(self, placeholder):
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=self.width)
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<FocusOut>", lambda e: self.after(150, self._fechar_dropdown))

    def _on_key(self, event):
        texto = self.entry.get().lower()

        if hasattr(self, "_dropdown") and self._dropdown.winfo_exists():
            self._dropdown.destroy()

        if not texto:
            return

        filtrados = [v for v in self.valores if texto in v.lower()][:10]
        if not filtrados:
            return

        self._dropdown = ctk.CTkToplevel(self)
        self._dropdown.overrideredirect(True)
        self._dropdown.attributes("-topmost", True)

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self._dropdown.geometry(f"{self.width}x{min(len(filtrados) * 36, 250)}+{x}+{y}")

        frame = ctk.CTkScrollableFrame(self._dropdown, width=self.width - 20)
        frame.pack(fill="both", expand=True)

        for item in filtrados:
            btn = ctk.CTkButton(frame, text=item, anchor="w",
                fg_color="transparent", hover_color="#2b2b2b",
                command=lambda i=item: self._selecionar(i))
            btn.pack(fill="x", pady=1)

    def _fechar_dropdown(self):
        if hasattr(self, "_dropdown") and self._dropdown.winfo_exists():
            self._dropdown.destroy()

    def _selecionar(self, valor):
        self.entry.delete(0, "end")
        self.entry.insert(0, valor)
        self._fechar_dropdown()
        if self.ao_selecionar:
            self.ao_selecionar(valor)

    def get(self):
        return self.entry.get()

    def set(self, valor):
        self.entry.delete(0, "end")
        self.entry.insert(0, valor)

    def clear(self):
        self.entry.delete(0, "end")

    def focus(self):
        self.entry.focus()