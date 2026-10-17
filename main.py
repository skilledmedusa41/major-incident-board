import tkinter as tk

from nr_board import NRIncidentBoard

root = tk.Tk()
root.title("Major Incident Board")
root.geometry("1150x720")
root.minsize(950, 600)

app = NRIncidentBoard(root)
app.pack(fill="both", expand=True)

root.mainloop()
