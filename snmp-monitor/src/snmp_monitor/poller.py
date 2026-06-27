from datetime import datetime

from snmp_monitor.models import AgentConfig, InterfaceMetric
from snmp_monitor.oid import IF_OPER_STATUS, INTERFACE_METRIC_COLUMNS
from snmp_monitor.snmp_client import snmp_walk


def _to_int(value, default: int = 0) -> int: 
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def poll_interfaces(agent: AgentConfig) -> list[InterfaceMetric]:
    """
    Legge la ifTable di un agente SNMP e costruisce una metrica per ogni interfaccia.
    """

    columns = {} # Metto i risultati delle walk

    for name, oid in INTERFACE_METRIC_COLUMNS.items(): # Esegue una walk per ogni colonna della tabella
        columns[name] = snmp_walk(
            agent.host,
            agent.port,
            agent.community,
            oid.value,
        )

    metriche = [] # Metriche per una interfaccia
    timestamp = datetime.now()
    interface_indexes = columns["ifDescr"].keys() # Prende gli indici delle interfacce usando ifDescr

    for if_index in interface_indexes: # Costruisco la riga InterfaceMetric per ogni interfaccia
        statusCode = _to_int(columns["ifOperStatus"].get(if_index)) 

        misura = InterfaceMetric(
            timestamp = timestamp,
            agent = agent.name,
            if_index = if_index,
            if_name = columns["ifDescr"].get(if_index, ""),
            if_status = IF_OPER_STATUS.get(statusCode, "unknown"),
            in_octets = _to_int(columns["ifInOctets"].get(if_index)),
            out_octets = _to_int(columns["ifOutOctets"].get(if_index)),
            in_errors = _to_int(columns["ifInErrors"].get(if_index)),
            out_errors = _to_int(columns["ifOutErrors"].get(if_index)),
        )
        metriche.append(misura)
        
    return metriche

