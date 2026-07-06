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
    for trap in traps:
        # Considero solo le trap che provengono dall'agente che sto graficando
        if trap["source_ip"] == agent_ip:
            # Prendo il colore associato al tipo di trap
            # Se il tipo non è nella mappa uso bianco come default
            color = colors.get(trap["trap_type"], "#FFFFFF")
            # datetime.fromisoformat() lo converte in oggetto datetime
            # .timestamp() lo trasforma in Unix timestamp
            ts = int(datetime.datetime.fromisoformat(trap["timestamp"]).timestamp())
            # Costruisco la stringa VRULE nel formato richiesto da rrdtool:
            # VRULE:timestamp#colore:etichetta
            vrules.append(f"VRULE:{ts}{color}:{trap['trap_type']}")
    return vrules