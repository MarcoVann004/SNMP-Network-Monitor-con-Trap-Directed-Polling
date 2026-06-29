import asyncio
import logging
from datetime import datetime
from typing import Optional

from snmp_monitor.models import AgentConfig, InterfaceMetric, COUNTER32_MAX
from snmp_monitor.oid import IF_OPER_STATUS, INTERFACE_METRIC_COLUMNS
from snmp_monitor.snmp_client import snmp_bulk_walk


# Logger per il modulo
logger = logging.getLogger(__name__)



def _to_int(value, field_name: str = "", default: int = 0) -> int:
    """
    Converte il valore stringa restituito da pysnmp in intero. Logga un warning se il valore non è parsabile
    """
    
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        if field_name:
            logger.warning(
                "Valore non parsabile per %s: %r — uso default %d",
                field_name, value, default
            )
        return default


async def poll_interface(agent: AgentConfig) -> list[InterfaceMetric]:
    """
    Legge la ifTable di un agente SNMP e costruisce una metrica per ogni interfaccia.
    """

    try:
        risultati = await asyncio.gather(
            *[
                snmp_bulk_walk(agent.host, agent.port, agent.community, oid.value)
                for oid in INTERFACE_METRIC_COLUMNS.values()
            ],
            return_exceptions = True # Se fallisce una lettura non annulla tutte le altre
        )
    except Exception as exc:
        logger.error("Errore imprevisto durante il polling di %s: %s", agent.name, exc)
        return []
    
    # Ricostruisce il dizionario {if_index: valore}
    columns: dict[str, dict[int, str]] = {}
    
    # zip(...) permette di unire i risulati ricevuti dal gather (i valori) alle chiavi (IfDescr, IfInOctets...)
    for col_name, result in zip(INTERFACE_METRIC_COLUMNS.keys(), risultati):
        if isinstance(result, Exception): # Se una lettura non è avvenuta aggiunge solo {}
            logger.warning(
                "[%s] Walk fallita per colonna %s: %s — colonna ignorata",
                agent.name, col_name, result
            )
            columns[col_name] = {}
        else:
            columns[col_name] = result
    
    metriche: list[InterfaceMetric] = []
    timestamp = datetime.now()

    # Usa gli indici della colonna ifDescr come riferimento
    interface_indexes = columns["ifDescr"].keys()

    for if_index in interface_indexes:
        status_code = _to_int(columns["ifOperStatus"].get(if_index))

        metrica = InterfaceMetric(
            timestamp=timestamp,
            agent=agent.name,
            if_index=if_index,
            if_name=columns["ifDescr"].get(if_index, ""),
            if_status=IF_OPER_STATUS.get(status_code, "unknown"),
            in_octets=_to_int(columns["ifInOctets"].get(if_index)),
            out_octets=_to_int(columns["ifOutOctets"].get(if_index)),
            in_errors=_to_int(columns["ifInErrors"].get(if_index)),
            out_errors=_to_int(columns["ifOutErrors"].get(if_index)),
        )

        metriche.append(metrica)

    return metriche        

def poller_mbps(agent: AgentConfig, interval: int = 5) -> list[InterfaceMetric]:
    """
    Esegue due polling a distanza di interval secondi e calcola la velocità in Mbps.
    """
    
    # I Mbps si può calcolare prendendo i valori di quanti byte sono entrati e usciti da una interfaccia di rete (che sono rispettivamente ifInOctets e ifOutOctets)
    # E applicando la formula: Mbps = ((octets_attuali - octets_precedenti) * 8) / secondi_trascorsi / 1_000_000
    
    octes_precedenti = poll_interfaces(agent)
    time.sleep(interval)
    octes_attuali = poll_interfaces(agent)
    
    # Trasformo le metriche che ho raccolto in un dizionario
    # Affinché per accedere subito ai valori di quell'interfaccia
    
    previous_by_index = {
        metrica.if_index: metrica
        for metrica in octes_precedenti
    }
    
    metriche = []
    
    for current in octes_attuali:
        previous = previous_by_index.get(current.if_index)
        
        if previous is None:
            metriche.append(current)
            continue
        
        # Calcolo il tempo trascorso fra le due letture
        delta_time = (current.timestamp - previous.timestamp).total_seconds()
        
        # Calcolo i byte ricevuti tra la prima e la seconda lettura
        delta_in = current.in_octets - previous.in_octets
        
        # Calcolo i byte inviati tra la prima e la seconda lettura
        delta_out = current.out_octets - previous.out_octets
        
        if delta_time <= 0 or delta_in < 0 or delta_out < 0:
            in_mbps = 0.0
            out_mbps = 0.0
        else:
            in_mbps = (delta_in * 8) / delta_time / 1_000_000
            out_mbps = (delta_out * 8) / delta_time / 1_000_000
        
        # Inserisco i valori calcolati nelle metriche
        misura = InterfaceMetric(
            timestamp=current.timestamp,
            agent=current.agent,
            if_index=current.if_index,
            if_name=current.if_name,
            if_status=current.if_status,
            in_octets=current.in_octets,
            out_octets=current.out_octets,
            in_errors=current.in_errors,
            out_errors=current.out_errors,
            in_mbps=round(in_mbps, 4),
            out_mbps=round(out_mbps, 4),
        )
        
        metriche.append(misura)
    
    return metriche


# Devo aggiungere la funzione che chiama i poll_interfaces