import json
import random
import statistics
from datetime import datetime, timedelta

NR_PRIORITIES = ["P1", "P2", "P3", "P4"]
NR_STATUSES = ["Nyitott", "Vizsgálat alatt", "Elhárítva"]
NR_SERVICES = ["Webshop", "E-mail", "VPN", "Adatbázis", "Hálózat", "SAP", "Active Directory"]
NR_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

NR_ALERTS = [
    ("Webshop", "A fizetési oldal 500-as hibát ad"),
    ("E-mail", "Levelek nem érkeznek meg a külső címekről"),
    ("VPN", "A távoli dolgozók nem tudnak csatlakozni"),
    ("Adatbázis", "Lassú lekérdezések, magas CPU terhelés"),
    ("Hálózat", "Csomagvesztés a központi switchen"),
    ("SAP", "A számlázó modul nem indul"),
    ("Active Directory", "Sikertelen bejelentkezések tömegesen"),
]


class NRIncident:
    def __init__(self, number, title, service, priority, opened=None, status="Nyitott", resolved=None, timeline=None):
        self.number = number
        self.title = title
        self.service = service
        self.priority = priority
        self.opened = opened or datetime.now()
        self.status = status
        self.resolved = resolved
        self.timeline = timeline or [(self.opened.strftime(NR_TIME_FORMAT), "Incidens megnyitva")]

    @property
    def code(self):
        return f"INC{self.number:05d}"

    def is_open(self):
        return self.resolved is None

    def add_update(self, text):
        self.timeline.append((datetime.now().strftime(NR_TIME_FORMAT), text))

    def set_status(self, status):
        if status == self.status:
            return
        self.status = status
        self.add_update(f"Státusz módosítva: {status}")
        if status == "Elhárítva":
            self.resolved = datetime.now()
        else:
            self.resolved = None

    def duration_minutes(self):
        end = self.resolved or datetime.now()
        return (end - self.opened).total_seconds() / 60

    def to_dict(self):
        return {
            "number": self.number,
            "title": self.title,
            "service": self.service,
            "priority": self.priority,
            "status": self.status,
            "opened": self.opened.strftime(NR_TIME_FORMAT),
            "resolved": self.resolved.strftime(NR_TIME_FORMAT) if self.resolved else None,
            "timeline": self.timeline,
        }

    @classmethod
    def from_dict(cls, data):
        resolved = data.get("resolved")
        return cls(
            data["number"],
            data["title"],
            data["service"],
            data["priority"],
            opened=datetime.strptime(data["opened"], NR_TIME_FORMAT),
            status=data["status"],
            resolved=datetime.strptime(resolved, NR_TIME_FORMAT) if resolved else None,
            timeline=[tuple(entry) for entry in data["timeline"]],
        )


def nr_format_duration(minutes):
    hours, mins = divmod(int(minutes), 60)
    return f"{hours} ó {mins:02d} p"


def nr_priority_color(priority, light=False):
    strong = {"P1": "#c62828", "P2": "#ef6c00", "P3": "#f9a825", "P4": "#2e7d32"}
    pale = {"P1": "#ffcdd2", "P2": "#ffe0b2", "P3": "#fff9c4", "P4": "#c8e6c9"}
    return (pale if light else strong).get(priority, "#e0e0e0")


def nr_random_incident(number):
    service, title = random.choice(NR_ALERTS)
    priority = random.choices(NR_PRIORITIES, weights=[1, 2, 3, 3])[0]
    opened = datetime.now() - timedelta(minutes=random.randint(5, 240))
    return NRIncident(number, title, service, priority, opened=opened)


def nr_statistics(incidents):
    durations = [incident.duration_minutes() for incident in incidents if not incident.is_open()]
    services = [incident.service for incident in incidents]
    result = {"mean": 0, "median": 0, "stdev": 0, "top_service": "-"}
    if durations:
        result["mean"] = statistics.mean(durations)
        result["median"] = statistics.median(durations)
        result["stdev"] = statistics.pstdev(durations)
    if services:
        result["top_service"] = statistics.mode(services)
    return result


def nr_save_incidents(path, incidents):
    with open(path, "w", encoding="utf-8") as file:
        json.dump([incident.to_dict() for incident in incidents], file, ensure_ascii=False, indent=2)


def nr_load_incidents(path):
    try:
        with open(path, encoding="utf-8") as file:
            return [NRIncident.from_dict(data) for data in json.load(file)]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []
