"""
05_localizador-hosts.py - Localizador de hosts del Network Controller

Dada una IP, una MAC o un nombre de host, muestra en qué equipo de red
(switch o router), en qué interfaz y en qué VLAN está conectado.
Sin argumentos, lista la ubicación de todos los hosts que ve el controlador.

Uso:
    python 05_localizador-hosts.py                    # todos los hosts
    python 05_localizador-hosts.py 192.168.10.11      # por IP
    python 05_localizador-hosts.py 0001.96B3.7B03     # por MAC (cualquier formato)
    python 05_localizador-hosts.py PC1                # por nombre

Exportar a CSV: agregar --csv (opcionalmente con el nombre del archivo).
    python 05_localizador-hosts.py --csv              # todos -> hosts.csv
    python 05_localizador-hosts.py PC1 --csv pc1.csv  # búsqueda -> pc1.csv

"""

import csv
import json
import os
import re
import sys

import requests
from tabulate import tabulate

BASE_URI = "http://localhost:58000/api/v1"

# Credenciales del Network Controller del grupo (las mismas del informe y los rótulos).
# Si en tu controlador creaste otro usuario, cambialas acá.
USUARIO = "cisco"
CLAVE = "class"


# ------------------------------------------------------------------------ API
def pedir_ticket(usuario, clave):
    """POST /ticket -> devuelve el serviceTicket para el header X-Auth-Token."""
    resp = requests.post(
        BASE_URI + "/ticket",
        data=json.dumps({"username": usuario, "password": clave}),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    if resp.status_code != 201 and resp.status_code != 200:
        sys.exit(f"Error al pedir el ticket (HTTP {resp.status_code}). ¿Usuario o clave incorrectos?")
    return resp.json()["response"]["serviceTicket"]


def get(endpoint, ticket):
    resp = requests.get(BASE_URI + endpoint, headers={"X-Auth-Token": ticket}, timeout=10)
    if resp.status_code != 200:
        sys.exit(f"Error en GET {endpoint} (HTTP {resp.status_code})")
    return resp.json()["response"]


# ------------------------------------------------------------------- búsqueda
def normalizar_mac(mac):
    """'0001.96B3.7B03', '00:01:96:b3:7b:03' y '00-01-96-B3-7B-03' -> '000196b37b03'."""
    return re.sub(r"[^0-9a-f]", "", (mac or "").lower())


def es_mac(texto):
    return len(normalizar_mac(texto)) == 12 and not re.fullmatch(r"[\d.]+", texto)


def buscar(hosts, criterio):
    criterio = criterio.strip()
    if es_mac(criterio):
        objetivo = normalizar_mac(criterio)
        return [h for h in hosts if normalizar_mac(h.get("hostMac")) == objetivo]
    por_ip = [h for h in hosts if h.get("hostIp") == criterio]
    if por_ip:
        return por_ip
    return [h for h in hosts if (h.get("hostName") or "").lower() == criterio.lower()]


def nombre_equipo(host, por_ip, por_id):
    """Traduce la IP/ID del equipo al que está conectado el host a su hostname."""
    equipo = por_id.get(host.get("connectedNetworkDeviceId")) or por_ip.get(
        host.get("connectedNetworkDeviceIpAddress")
    )
    if equipo:
        return equipo.get("hostname") or "?"
    return "(no administrado)"


def ubicacion(host, por_ip, por_id):
    return {
        "Host": host.get("hostName", "?"),
        "Tipo": host.get("hostType", "?"),
        "IP": host.get("hostIp", "?"),
        "MAC": host.get("hostMac", "?"),
        "Equipo": nombre_equipo(host, por_ip, por_id),
        "IP del equipo": host.get("connectedNetworkDeviceIpAddress", "?"),
        "Interfaz": host.get("connectedInterfaceName", "?"),
        "VLAN": host.get("vlanId") or "-",
    }


# ------------------------------------------------------------------------ CSV
def leer_argumentos(argv):
    """Separa el criterio de búsqueda de la opción --csv [archivo]."""
    args = list(argv)
    archivo_csv = None
    if "--csv" in args:
        i = args.index("--csv")
        args.pop(i)
        if i < len(args) and args[i].lower().endswith(".csv"):
            archivo_csv = args.pop(i)
        else:
            archivo_csv = "hosts.csv"
    return " ".join(args).strip(), archivo_csv


def exportar_csv(filas, archivo):
    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()), delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"\nSe exportaron {len(filas)} hosts a {os.path.abspath(archivo)}")


# ----------------------------------------------------------------------- main
def main():
    criterio, archivo_csv = leer_argumentos(sys.argv[1:])

    try:
        ticket = pedir_ticket(USUARIO, CLAVE)
        hosts = get("/host", ticket)
        equipos = get("/network-device", ticket)
    except requests.exceptions.ConnectionError:
        sys.exit(f"No se pudo conectar a {BASE_URI}. ¿Está abierto Packet Tracer con el controlador?")

    por_ip = {e.get("managementIpAddress"): e for e in equipos}
    por_id = {e.get("id"): e for e in equipos}

    if not criterio:
        filas = [ubicacion(h, por_ip, por_id) for h in hosts]
        filas.sort(key=lambda f: (f["Equipo"], f["Interfaz"]))
        print(f"\nUbicación de los {len(filas)} hosts que ve el controlador:\n")
        print(tabulate(filas, headers="keys", tablefmt="rst"))
        if archivo_csv and filas:
            exportar_csv(filas, archivo_csv)
        return

    encontrados = buscar(hosts, criterio)
    if not encontrados:
        print(f"\nNo se encontró ningún host con '{criterio}'.")
        print("Hosts conocidos:", ", ".join(sorted(h.get("hostName", "?") for h in hosts)))
        sys.exit(1)

    for host in encontrados:
        datos = ubicacion(host, por_ip, por_id)
        vlan = f", VLAN {datos['VLAN']}" if datos["VLAN"] != "-" else ""
        print(f"\n{datos['Host']} ({datos['IP']}) está conectado a "
              f"{datos['Equipo']}, interfaz {datos['Interfaz']}{vlan}.\n")
        print(tabulate(datos.items(), tablefmt="rst"))

    if archivo_csv:
        exportar_csv([ubicacion(h, por_ip, por_id) for h in encontrados], archivo_csv)


if __name__ == "__main__":
    main()