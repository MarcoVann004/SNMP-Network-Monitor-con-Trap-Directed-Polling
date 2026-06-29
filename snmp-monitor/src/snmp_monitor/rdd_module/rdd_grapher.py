import os
import rrdtool

def graph_traffic(path:str) :

    os.makedirs("rrd_graphs", exist_ok=True)

    rrd_path = f"rrd_data/{path}"
    png_path = f"rrd_graphs/{path.replace('.rrd', '.png')}"

    rrd_path_abs = os.path.abspath(f"rrd_data/{path}")
    print(f"File esiste: {os.path.exists(rrd_path_abs)}")
    print(f"DEF: DEF:traffic_in:{rrd_path_abs}:if_octets_in:AVERAGE")

    rrdtool.graph(
        png_path,
        "--start","-24h",
        "--end","now",
        "--title", "Traffico eth0" ,      # titolo del grafico
        "--vertical-label", "bytes/s",     # etichetta asse Y
        "--width", "800",                  # larghezza in pixel
        "--height", "300",                 # altezza in pixel
        f"DEF:traffic_in={rrd_path_abs}:if_octets_in:AVERAGE",
        f"DEF:traffic_out={rrd_path_abs}:if_octets_out:AVERAGE",
        "LINE1:traffic_in#0000FF:Traffico In",    # linea blu
        "AREA:traffic_out#00FF0080:Traffico Out", # area verde semitrasparente
    )

def generate_all_graph() :
        
    os.makedirs("rrd_graphs", exist_ok=True) 
    lista=[f for f in os.listdir("rrd_data/") if f.endswith(".rrd")]

    for file in lista :
        graph_traffic(file)


if __name__ == "__main__" :
    generate_all_graph()