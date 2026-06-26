import random
import config
import csv
import os
import time

MAX_COUNTER_32 = 2**32

# Stato iniziale degli agenti simulati
AGENTS = {
    "192.168.1.1": {
        "interfaces": [
            {
                "if_index": 1,
                "if_descr": "eth0",
                "if_in_octets": random.randint(0, 10_000_000),
                "if_out_octets": random.randint(0, 10_000_000),
                "if_in_errors": 0,
                "if_out_errors": 0,
                "if_oper_status": 1,
                "base_in_mbps": 10.0,   # traffico simulato medio
                "base_out_mbps": 5.0,
            },
            {
                "if_index": 2,
                "if_descr": "eth1",
                "if_in_octets": random.randint(0, 5_000_000),
                "if_out_octets": random.randint(0, 5_000_000),
                "if_in_errors": 0,
                "if_out_errors": 0,
                "if_oper_status": 1,
                "base_in_mbps": 2.0,
                "base_out_mbps": 2.0,
            },
        ]
    }
}

def generatore_incremento_traffico(base_mbps:float , variance :float =0.2) -> int :

    #simula l'incremento di byte in un intervallo di polling.
    #base_mbps: traffico medio simulato
    #variance: variazione casuale (0.2 = ±20%)

    noise = random.uniform(1-variance,1+variance)
    mbps= base_mbps * noise
    byte= (mbps * 1000000)/ 8
    return int(byte*config.POLLING_INTERVAL)

def simulate_oper_status(stato_corrente:int , prob_fallimento:float = 0.02) -> int :
    
    #cambio randomico dello stato 1 = up , 2 = down

    if stato_corrente == 1 and random.random() < prob_fallimento:
        return 2  # va down
    elif stato_corrente == 2 and random.random() < 0.3:
        return 1  # torna up
    return stato_corrente

def generate_error_increment(prob_err:float= 0.05) -> int : 

    #errore casuale
    
    if random.random() < prob_err :
        return random.randint(1,5)
    return 0

def wrap_counter(value: int) -> int:
    return value % MAX_COUNTER_32

def write_metrics(filepath: str , rows: list[dict]) -> None :
    file_exist= os.path.exists(filepath)
    with open(filepath , "a" ,newline=" ") as f:
        fieldnames = [
            "timestamp", "agent_ip", "if_index", "if_descr",
            "if_in_octets", "if_out_octets",
            "if_in_errors", "if_out_errors", "if_oper_status"
        ]
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        if not file_exist:
            writer.writeheader()
        writer.writerows(rows)