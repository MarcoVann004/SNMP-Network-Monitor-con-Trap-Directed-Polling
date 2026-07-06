import os
import csv
import datetime

def load_traps(csv_path: str) -> list:
    traps = []
    if not os.path.exists(csv_path):
        return traps
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            traps.append(row)
    return traps

def get_vrules(traps: list, agent_ip: str) -> list:
    # Colori associati a ogni tipo di trap
    colors = {
        "linkDown": "#FF0000", # rosso — interfaccia giù
        "linkUp": "#00FF00",   # verde — interfaccia tornata su
        "coldStart": "#FFA500",# arancione — riavvio freddo
        "warmStart": "#FFA500",# arancione — riavvio caldo
        "authenticationFailure": "#FFFF00",  # giallo — errore autenticazione
    }
    vrules = []

    # Filtra le trap rilevanti per l'agente (incluso "unknown") e parse timestamp
    relevant = []
    for trap in traps:
        src = trap.get("source_ip", "")
        if src == agent_ip or src == "unknown":
            try:
                ts = int(datetime.datetime.fromisoformat(trap["timestamp"]).timestamp())
            except Exception:
                continue
            relevant.append((ts, trap.get("trap_type"), trap))

    # Ordino per timestamp; etichetto solo la prima occorrenza di ogni tipo di trap.
    relevant.sort(key=lambda x: x[0])
    seen_types = set()
    for ts, ttype, trap in relevant:
        color = colors.get(ttype, "#FFFFFF")
        if ttype in seen_types:
            vrules.append(f"VRULE:{ts}{color}")
        else:
            seen_types.add(ttype)
            vrules.append(f"VRULE:{ts}{color}:{ttype}")

    return vrules
