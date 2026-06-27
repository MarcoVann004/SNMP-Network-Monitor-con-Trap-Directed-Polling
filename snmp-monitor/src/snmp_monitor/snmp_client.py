# Questo file esegue richieste SNMP (GET e WALK)

import asyncio
from pysnmp.hlapi.asyncio import bulk_walk_cmd, SnmpEngine, CommunityData, UdpTransportTarget, ObjectType, ObjectIdentity


# Siccome le richieste effettuate sono asincrone, definisco due funzioni una semplice che è possibile chiamare da qualunque parte e la sua versione asincrona viene eseguita internamente

def snmp_walk(host: str, port: int, community: str, oid: str): 
    """
    Esegue una richiesta SNMP WALK verso l'agente specificato.
    """
    return asyncio.run(snmp_walk_asincrona(host, port, community, oid))



async def snmp_walk_asincrona(host:str, port:int, community:str, oid:str):
    
    risultati = {}
    
    communicationChannel = await UdpTransportTarget.create((host, port)) # Crea il canale di comunicazione verso l'agent
    
    for errorIndication, errorStatus, varBinds in bulk_walk_cmd(
        SnmpEngine(), # Gestisce il ciclo di vita del pacchetto
        CommunityData(community, mpModel = 1), # Descrive il tipo di operazione da fare in questo caso GETBULK (con mpModel = 1)
        communicationChannel, # Specifico dove si trova l'agent
        0,
        25, # Numero massimo di ripetizioni che voglio ricevere da GETBULK
        ObjectType(ObjectIdentity(oid)), # Rappresenta l'OID che voglio leggere
        lexicographicMode = False, # Dice alla WALK di fermarsi quando esce dal sottoalbero
        lookupMib=False # Non provare a tradurre gli OID numerici usando i nomi delle MIB
    ):
        
        if errorIndication: # Errori di comunicazione (timeout, agent non raggiungibile ecc.)
            raise RuntimeError(errorIndication)
        
        if errorStatus: # Errore restituito dall'agente (OID inesistente ecc.)
            raise RuntimeError(errorStatus)

        # varBinds contiene la risposta restituita dall'agent con questa struttura: (OID_risposto, valore)
        for oidResponse, value in varBinds:
            oidResponse = str(oidResponse)
            
            if not oidResponse.startswith(oid + "."):
                continue
        
            idx = int(oidResponse.removeprefix(oid + "."))
            risultati[idx] = value.prettyPrint() # Salvo il valore nel dizionario
    
    return risultati