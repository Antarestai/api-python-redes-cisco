# API del Network Controller con Python

Scripts de Python que consumen la API REST (Northbound API) del Network Controller de Cisco Packet Tracer.
Trabajo Práctico N° 4 Integrador – Redes de Computadoras (3643), UNLaM 2026.

Los scripts `01` a `04` son los suministrados por la cátedra. El `05` es el script propio del grupo.

## Scripts

| Script | Endpoints | Qué hace |
|---|---|---|
| `01_get-ticket.py` | `POST /ticket` | Se autentica con el usuario y la clave del controlador y muestra el *service ticket* que después se usa en el header `X-Auth-Token`. |
| `02_get-network-device.py` | `GET /network-device` | Lista los equipos de red que administra el controlador: hostname, plataforma e IP de gestión. Muestra también la respuesta JSON completa. |
| `03_get-host.py` | `GET /host` | Lista los hosts de la red (PCs y servidores): nombre, IP, MAC e interfaz a la que están conectados. Muestra también la respuesta JSON completa. |
| `04_tabulate.py` | `POST /ticket`, `GET /network-device`, `GET /host` | Pide el ticket por su cuenta y muestra, en dos tablas, los equipos de red (hostname, número de serie y versión de IOS) y los hosts (nombre, tipo e IP). |
| `05_localizador-hosts.py` | `POST /ticket`, `GET /host`, `GET /network-device` | **Script propio.** Localiza los hosts en la red: indica a qué equipo (por su nombre), interfaz y VLAN está conectado cada uno. Permite buscar un host puntual y exportar el resultado a CSV. |

### 05_localizador-hosts.py (script propio)

Cruza las respuestas de `/host` y `/network-device` para mostrar dónde está conectado cada host: el nombre del switch o router, su IP de gestión, la interfaz y la VLAN. A diferencia de `02` y `03`, pide el ticket automáticamente, sin tener que copiarlo a mano.

```bash
python src/05_localizador-hosts.py                     # todos los hosts
python src/05_localizador-hosts.py PC1                 # buscar por nombre
python src/05_localizador-hosts.py 192.168.10.11       # buscar por IP
python src/05_localizador-hosts.py 0001.96B3.7B03      # buscar por MAC (cualquier formato)
python src/05_localizador-hosts.py --csv               # exportar todos a hosts.csv
python src/05_localizador-hosts.py PC1 --csv pc1.csv   # exportar una búsqueda
```

# Entorno de virtualización Python

# Pasos de instalación en Linux:

## 1. Clonación del proyecto

Desde la terminal ejecutar:

**git clone** <URL_del_repositorio> <nombre_de_la_carpeta_de_destino>

Luego ejecutar **cd** <nombre_de_la_carpeta_de_destino>. Esta carpeta será la raíz de nuestro proyecto en Python.

## 2. Creación del entorno virtual

Supongamos que el nombre que le damos al entorno virtual es **cisco**, entonces se creará una carpeta **cisco** con todas las librerías y dependencias necesarias paea nuestro proyecto. 

La manera de realizarlo es la siguiente:

# python3 -m venv <nombre_del_entorno>
Ejemplo: python3 -m venv cisco

Para activar el entorno escribimos **source cisco/bin/activate**, en la carpeta raíz del proyecto. El nombre del entorno virtual aparecerá entre paréntesis ().

## 3. Instalación de las dependencias, en este caso las librerías requests y tabulate

En la carpeta raíz de nuestro proyecto y dentro del entorno virtual escribimos: **pip install -r requirements.txt**

## 4. Selección del intérprete Python para nuestro entorno virtual

<img width="881" height="118" alt="image" src="https://github.com/user-attachments/assets/18c41d8e-d338-48b6-953c-b2499c57319f" />

<img width="736" height="412" alt="image" src="https://github.com/user-attachments/assets/2a795fcd-2cf8-47ef-a5a6-d21e09ce967f" />

Tal como se ve en la figura seleccionamos Python 3.10.12 (cisco) que se mostrará como entorno recomendado.

## 5. Desactivación del entorno virtual

Simplemente escribimos en la línea de comandos: **deactivate**



## Antes de ejecutar los scripts

- **Credenciales del controlador:** los scripts usan el usuario `cisco` y la clave `class`, que son las del controlador del grupo. Si en tu Network Controller creaste otro usuario, cambialos en `01_get-ticket.py`, `04_tabulate.py` y `05_localizador-hosts.py`.
- **Ticket (X-Auth-Token):** `02_get-network-device.py` y `03_get-host.py` traen escrito un ticket de ejemplo que **no va a funcionar** en tu Packet Tracer, porque el controlador genera uno nuevo en cada sesión y vence. Ejecutá primero `01_get-ticket.py`, copiá el ticket que muestra y reemplazalo en el header `X-Auth-Token` de esos dos scripts. `04_tabulate.py` y `05_localizador-hosts.py` no necesitan este paso: piden el ticket solos.
