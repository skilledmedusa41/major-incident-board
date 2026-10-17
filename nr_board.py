import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from nr_incident import (
    NR_PRIORITIES,
    NR_SERVICES,
    NR_STATUSES,
    NRIncident,
    nr_format_duration,
    nr_load_incidents,
    nr_priority_color,
    nr_random_incident,
    nr_save_incidents,
    nr_statistics,
)

NR_DATA_FILE = Path(__file__).with_name("incidents.json")


class NRIncidentBoard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, padx=10, pady=10)
        self.incidents = nr_load_incidents(NR_DATA_FILE)

        self.title_var = tk.StringVar()
        self.service_var = tk.StringVar(value=NR_SERVICES[0])
        self.priority_var = tk.StringVar(value="P3")
        self.status_var = tk.StringVar(value=NR_STATUSES[0])

        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=24)

        self.build_header()
        self.build_form()
        self.build_list()
        self.build_details()
        self.build_chart()

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.title_entry.bind("<Return>", lambda event: self.create_incident())
        self.chart.bind("<Configure>", lambda event: self.draw_chart())
        master.bind("<Control-n>", lambda event: self.title_entry.focus_set())
        master.bind("<F5>", lambda event: self.simulate_alert())
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.refresh()
        self.tick()

    def build_header(self):
        self.header = tk.Label(self, font=("Helvetica", 18, "bold"), fg="white", pady=8)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.clock = tk.Label(self.header, font=("Helvetica", 12), fg="white")
        self.clock.place(relx=1.0, rely=0.5, x=-10, anchor="e")

    def build_form(self):
        form = ttk.LabelFrame(self, text="Új incidens", padding=8)
        form.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(form, text="Leírás:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(form, textvariable=self.title_var, width=45)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Szolgáltatás:").grid(row=0, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.service_var, values=NR_SERVICES, state="readonly", width=16).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Prioritás:").grid(row=0, column=4, sticky="w")
        ttk.Combobox(form, textvariable=self.priority_var, values=NR_PRIORITIES, state="readonly", width=4).grid(row=0, column=5, padx=5)

        ttk.Button(form, text="Megnyitás", command=self.create_incident).grid(row=0, column=6, padx=5)
        ttk.Button(form, text="Szimulált riasztás (F5)", command=self.simulate_alert).grid(row=0, column=7, padx=5)

    def build_list(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = {"code": ("Azonosító", 90), "priority": ("Prio", 50), "title": ("Leírás", 260),
                   "service": ("Szolgáltatás", 120), "status": ("Státusz", 110), "duration": ("Időtartam", 90)}
        self.tree = ttk.Treeview(frame, columns=list(columns), show="headings", selectmode="browse")
        for key, (text, width) in columns.items():
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="w")
        for priority in NR_PRIORITIES:
            self.tree.tag_configure(priority, background=nr_priority_color(priority, light=True))
        self.tree.tag_configure("resolved", background="#eeeeee", foreground="#757575")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def build_details(self):
        frame = ttk.LabelFrame(self, text="Részletek és idővonal", padding=8)
        frame.grid(row=2, column=1, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        self.detail_label = ttk.Label(frame, text="Válassz ki egy incidenst a listából.", font=("Helvetica", 12, "bold"))
        self.detail_label.grid(row=0, column=0, columnspan=3, sticky="w")

        self.timeline = tk.Text(frame, height=12, width=40, wrap="word", state="disabled")
        self.timeline.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)

        ttk.Combobox(frame, textvariable=self.status_var, values=NR_STATUSES, state="readonly", width=15).grid(row=2, column=0, sticky="w")
        ttk.Button(frame, text="Státusz beállítása", command=self.change_status).grid(row=2, column=1, padx=5)
        ttk.Button(frame, text="Bejegyzés hozzáadása", command=self.add_update).grid(row=2, column=2)

    def build_chart(self):
        frame = ttk.LabelFrame(self, text="Nyitott incidensek prioritás szerint és MTTR statisztika", padding=8)
        frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        frame.columnconfigure(0, weight=1)

        self.chart = tk.Canvas(frame, height=140, bg="white", highlightthickness=0)
        self.chart.grid(row=0, column=0, sticky="ew")
        self.stats_label = ttk.Label(frame, font=("Helvetica", 11))
        self.stats_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

    def next_number(self):
        return max((incident.number for incident in self.incidents), default=0) + 1

    def selected_incident(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return next((incident for incident in self.incidents if incident.code == selection[0]), None)

    def create_incident(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Hiányzó adat", "Add meg az incidens leírását!", parent=self)
            return
        self.add_incident(NRIncident(self.next_number(), title, self.service_var.get(), self.priority_var.get()))
        self.title_var.set("")

    def simulate_alert(self):
        incident = nr_random_incident(self.next_number())
        self.add_incident(incident)
        if incident.priority == "P1":
            self.bell()

    def add_incident(self, incident):
        self.incidents.append(incident)
        self.refresh()
        self.tree.selection_set(incident.code)
        self.tree.see(incident.code)

    def change_status(self):
        incident = self.selected_incident()
        if incident is None:
            messagebox.showinfo("Nincs kiválasztva", "Előbb válassz ki egy incidenst!", parent=self)
            return
        incident.set_status(self.status_var.get())
        self.refresh()

    def add_update(self):
        incident = self.selected_incident()
        if incident is None:
            messagebox.showinfo("Nincs kiválasztva", "Előbb válassz ki egy incidenst!", parent=self)
            return
        text = simpledialog.askstring("Új bejegyzés", f"{incident.code} – mi történt?", parent=self)
        if text and text.strip():
            incident.add_update(text.strip())
            self.refresh()

    def on_select(self, event):
        incident = self.selected_incident()
        if incident:
            self.status_var.set(incident.status)
        self.show_details()

    def on_double_click(self, event):
        if self.tree.identify_row(event.y):
            self.add_update()

    def refresh(self):
        selection = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for incident in sorted(self.incidents, key=lambda item: (not item.is_open(), item.priority, item.number)):
            tag = incident.priority if incident.is_open() else "resolved"
            values = (incident.code, incident.priority, incident.title, incident.service,
                      incident.status, nr_format_duration(incident.duration_minutes()))
            self.tree.insert("", "end", iid=incident.code, values=values, tags=(tag,))
        if selection and self.tree.exists(selection[0]):
            self.tree.selection_set(selection[0])
        self.show_details()
        self.update_header()
        self.draw_chart()
        self.update_stats()
        nr_save_incidents(NR_DATA_FILE, self.incidents)

    def show_details(self):
        incident = self.selected_incident()
        self.timeline.configure(state="normal")
        self.timeline.delete("1.0", "end")
        if incident is None:
            self.detail_label.configure(text="Válassz ki egy incidenst a listából.")
        else:
            self.detail_label.configure(text=f"{incident.code} · {incident.priority} · {incident.service}")
            self.timeline.insert("end", incident.title + "\n\n")
            for timestamp, text in incident.timeline:
                self.timeline.insert("end", f"{timestamp}  {text}\n")
        self.timeline.configure(state="disabled")

    def update_header(self):
        open_p1 = [incident for incident in self.incidents if incident.is_open() and incident.priority == "P1"]
        if open_p1:
            self.header.configure(text=f"AKTÍV MAJOR INCIDENS: {len(open_p1)} db", bg=nr_priority_color("P1"))
        else:
            self.header.configure(text="MAJOR INCIDENT BOARD – nincs aktív P1", bg="#37474f")
        self.clock.configure(bg=self.header.cget("bg"))

    def draw_chart(self):
        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 400)
        height = int(self.chart.cget("height"))
        counts = {priority: 0 for priority in NR_PRIORITIES}
        for incident in self.incidents:
            if incident.is_open():
                counts[incident.priority] += 1
        highest = max(max(counts.values()), 1)
        bar_width = width / (len(NR_PRIORITIES) * 2)
        for index, priority in enumerate(NR_PRIORITIES):
            x0 = bar_width * (index * 2 + 0.5)
            bar_height = (height - 40) * counts[priority] / highest
            self.chart.create_rectangle(x0, height - 20 - bar_height, x0 + bar_width, height - 20,
                                        fill=nr_priority_color(priority), outline="")
            self.chart.create_text(x0 + bar_width / 2, height - 8, text=priority, font=("Helvetica", 10, "bold"))
            self.chart.create_text(x0 + bar_width / 2, height - 28 - bar_height, text=str(counts[priority]))

    def update_stats(self):
        stats = nr_statistics(self.incidents)
        open_count = sum(1 for incident in self.incidents if incident.is_open())
        self.stats_label.configure(
            text=f"Nyitott: {open_count}  |  MTTR átlag: {nr_format_duration(stats['mean'])}  |  "
                 f"medián: {nr_format_duration(stats['median'])}  |  szórás: {nr_format_duration(stats['stdev'])}  |  "
                 f"leggyakoribb szolgáltatás: {stats['top_service']}")

    def tick(self):
        self.clock.configure(text=datetime.now().strftime("%H:%M:%S"))
        for incident in self.incidents:
            if incident.is_open() and self.tree.exists(incident.code):
                self.tree.set(incident.code, "duration", nr_format_duration(incident.duration_minutes()))
        self.after(1000, self.tick)

    def on_close(self):
        nr_save_incidents(NR_DATA_FILE, self.incidents)
        self.master.destroy()
