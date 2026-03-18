import customtkinter as ctk

class SearchBox(ctk.CTkFrame):
    def __init__(self, master, valores, placeholder="Pesquisar...", width=200, ao_selecionar=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.valores = valores
        self.ao_selecionar = ao_selecionar
        self.width = width
        self._dropdown = None
        self._construir(placeholder)

    def _construir(self, placeholder):
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=self.width)
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<FocusOut>", lambda e: self.after(200, self._fechar_dropdown))
        self.entry.bind("<Escape>", lambda e: self._fechar_dropdown())

    def _on_key(self, event):
        if event.keysym in ("Return", "Tab"):
            return

        texto = self.entry.get().lower()
        self._fechar_dropdown()

        if not texto:
            return

        filtrados = [v for v in self.valores if texto in v.lower()][:10]
        if not filtrados:
            return

        self._abrir_dropdown(filtrados)

    def _abrir_dropdown(self, itens):
        self._fechar_dropdown()

        root = self.winfo_toplevel()

        x = self.entry.winfo_rootx() - root.winfo_rootx()
        y = self.entry.winfo_rooty() - root.winfo_rooty() + self.entry.winfo_height()
        h = min(len(itens) * 36, 260)

        self._dropdown = ctk.CTkFrame(root,
            fg_color="#2b2b2b",
            corner_radius=6,
            border_width=1,
            border_color="#3a3a3a",
            width=self.width,
            height=h)

        self._dropdown.place(x=x, y=y)
        self._dropdown.pack_propagate(False)
        self._dropdown.lift()

        scroll = ctk.CTkScrollableFrame(self._dropdown, fg_color="transparent")
        scroll.place(x=0, y=0, relwidth=1, relheight=1)

        for item in itens:
            btn = ctk.CTkButton(scroll, text=item, anchor="w",
                fg_color="transparent", hover_color="#3a3a3a",
                text_color="#f0f0f0",
                command=lambda i=item: self._selecionar(i))
            btn.pack(fill="x", pady=1)

    def _fechar_dropdown(self):
        try:
            if self._dropdown and self._dropdown.winfo_exists():
                self._dropdown.place_forget()
                self._dropdown.destroy()
        except:
            pass
        self._dropdown = None

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