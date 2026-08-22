# Controle do Microsoft Flight Simulator 2024 (Python + SimConnect)

Programa em Python para **enviar comandos** e **automatizar rotinas** no
Microsoft Flight Simulator 2024, usando a API oficial **SimConnect**.

Com ele você pode, a partir de um script externo, acelerar os motores, mexer
no trem de pouso e flaps, controlar o piloto automático, luzes, e ainda
encadear tudo isso em **sequências automatizadas** (decolagem, preparação para
pouso, checklists).

## Como funciona

O MSFS expõe a API **SimConnect** (parte do SDK da Microsoft/Asobo). Um
programa externo se conecta ao simulador em execução e pode:

- **Disparar eventos** (comandos): `GEAR_UP`, `THROTTLE_SET`, `AP_MASTER`, etc.
- **Ler variáveis de simulação** (SimVars): velocidade, altitude, etc.

Este projeto envolve a biblioteca [`Python-SimConnect`](https://pypi.org/project/SimConnect/)
em uma API mais amigável.

## Requisitos

- **Windows** com o **Microsoft Flight Simulator 2024** instalado e rodando.
- **Python 3.9+**.
- A biblioteca `SimConnect` (instalada via `requirements.txt`). Ela usa o
  `SimConnect.dll` que acompanha o simulador/SDK.

> O simulador precisa estar **aberto e com uma sessão de voo carregada** para
> que a conexão funcione. O código foi escrito para importar sem erros em
> qualquer sistema operacional (inclusive Linux/macOS), mas os comandos só
> têm efeito conectado a um MSFS real no Windows.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso rápido — enviar comandos

```python
from msfs_control import MSFSController

with MSFSController() as msfs:
    msfs.set_parking_brake(False)   # libera o freio
    msfs.throttle(80)               # 80% de potência
    msfs.gear_up()                  # recolhe o trem
    msfs.flaps(0)                   # recolhe os flaps
    msfs.autopilot(True)            # liga o piloto automático
    msfs.set_altitude(10000)        # altitude alvo 10.000 ft
    msfs.set_heading(270)           # rumo 270°
```

Qualquer evento SimConnect não coberto pelos atalhos pode ser enviado direto:

```python
msfs.send_event("TOGGLE_MASTER_BATTERY")
```

## Uso — automação com sequências

```python
from msfs_control import MSFSController, Sequence, Step, wait_until

seq = Sequence("Decolagem", [
    Step("Liberar freio",   lambda m: m.set_parking_brake(False)),
    Step("Potência total",  lambda m: m.throttle_full()),
    Step("Esperar rotação", lambda m: wait_until(
        m, "AIRSPEED_INDICATED", lambda v: v >= 130)),
    Step("Recolher trem",   lambda m: m.gear_up()),
])

with MSFSController() as msfs:
    seq.run(msfs)
```

## Telemetria ao vivo no console

Painel que atualiza em tempo real com altitude, velocidade, posição, rumo e
atitude — sem dependências externas:

```bash
python -m scripts.live_telemetry           # 4 atualizações/segundo (padrão)
python -m scripts.live_telemetry --hz 5    # 5 atualizações/segundo
```

```
+--------------------------------------------------+
|          MSFS 2024 - TELEMETRIA AO VIVO          |
+--------------------------------------------------+
|  Estado        : EM VOO                          |
|  Altitude MSL  :       3500 ft                   |
|  Vel. indicada :        250 kt                   |
|  Rumo (mag)    :        272 deg                  |
|  Latitude      :   23.5432° S                    |
|  Longitude     :   46.6541° W                    |
+--------------------------------------------------+
```

Para uso programático, leia um snapshot com `TelemetryReader`:

```python
from msfs_control import SimConnection, TelemetryReader

with SimConnection() as conn:
    snap = TelemetryReader(conn).read()
    print(snap.altitude_ft, snap.airspeed_kt, snap.heading_deg)
    print(snap.as_dict())   # todos os campos como dicionário
```

## Scripts de exemplo prontos

Rode com o simulador aberto, a partir da raiz do projeto:

```bash
python -m scripts.live_telemetry  # painel de telemetria ao vivo
python -m scripts.demo_commands   # envia comandos simples de demonstração
python -m scripts.auto_takeoff    # sequência automatizada de decolagem
python -m scripts.landing_prep    # preparação automatizada para pouso
```

## Estrutura do projeto

```
msfs_control/
  connection.py   # conexão de baixo nível com o SimConnect
  controller.py   # API de alto nível para enviar comandos
  automation.py   # framework de sequências (Step, Sequence, wait_until)
  telemetry.py    # leitura de telemetria (Telemetry, TelemetryReader)
scripts/
  live_telemetry.py
  demo_commands.py
  auto_takeoff.py
  landing_prep.py
tests/
  test_conversions.py  # testes que rodam sem o simulador
  test_telemetry.py    # testes de telemetria (conexão falsa)
```

## Testes

Os testes de lógica pura rodam em qualquer sistema, sem o MSFS:

```bash
python -m unittest discover tests
```

## Aviso

Os scripts de automação (decolagem/pouso) são **exemplos educativos**. As
velocidades e configurações variam por aeronave — ajuste os valores antes de
usar. Não substituem o pilotar manual em fases críticas do voo.
