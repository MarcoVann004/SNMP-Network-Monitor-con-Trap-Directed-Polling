import time
import rrdtool
import os
import csv

def create_rrd_path(agent_ip:str,if_index:str)-> str :

    #crea il filename per l'agent 

    ip=agent_ip.replace(".","_")
    filename=f"rrd_data/{ip}_if{if_index}.rrd"
    return filename

def create_rrd(path:str) :

    #creo la cartella contenente i file rrd se esiste non succede altro

    os.makedirs("rrd_data", exist_ok=True) 

    #.create crea effettivamente il file rrd

    rrdtool.create(
        path,   #nome file
        "--step","60", # ogni quanto fa polling
        "DS:if_oper_status:GAUGE:120:0:U", #DS:nome:tipo:heartbeat:min:max (GAUGE per valori fissi, COUNTER per valori crescenti)
        "DS:if_octets_in:COUNTER:120:0:U",  #min valore minimo accettato per i contatori e max valore massimo, U per illimitato
        "DS:if_octets_out:COUNTER:120:0:U", #heartbeat è 2xstep quindi 60x2
        "DS:if_in_errors:COUNTER:120:0:U",
        "DS:if_out_errors:COUNTER:120:0:U",
        "RRA:AVERAGE:0.5:1:1440" # salva la media, ogni 1 misura, per 1440 campioni
    )

def update_rrd(path:str,row:dict) :

    #il file rrd esiste già vieni solo aggiornato

    stringa=f"{row['timestamp']}:{row['if_oper_status']}:{row['if_in_octets']}:{row['if_out_octets']}:{row['if_in_errors']}:{row['if_out_errors']}"
    print(f"UPDATE: {path} -> {stringa}")

    try:
        rrdtool.update(path, stringa)
    except rrdtool.OperationalError as e:
        print(f"Saltato: {e}")
        pass  # timestamp già inserito, saltiamo

def process_row(row:dict):

    #trovi il path e controlli se esiste

    path= create_rrd_path(row['agent_ip'],row['if_index'])

    if not os.path.exists(path): 
        create_rrd(path)
    update_rrd(path,row)


if __name__ == "__main__":
    with open("metrics.csv", "r") as f:
        reader = csv.DictReader(f)
        rows = sorted(reader, key=lambda r: int(r["timestamp"]))
        print(f"Righe lette: {len(rows)}")
        for row in rows:
            process_row(row)