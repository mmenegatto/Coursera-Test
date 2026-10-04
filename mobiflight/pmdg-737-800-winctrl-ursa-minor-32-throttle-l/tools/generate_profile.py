#!/usr/bin/env python3
"""
Gera o profile MobiFlight (.mfproj) do WINCTRL URSA MINOR 32 Throttle Metal L
para o PMDG 737-800 (MSFS 2024).

Uso:
    python3 generate_profile.py   # grava ../PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj

Modelo hibrido (como no profile da comunidade testado no sim):
  - MSFS 2024: manetes, reverso, eixo de speedbrake, rudder trim, parking brake
    (tabela no README). SimAppPro em "Double-stroke four-axle".
  - MobiFlight (este arquivo): o que e especifico do PMDG -- start levers,
    start switches, flaps, speedbrake ARM, A/T disengage, TO/GA, display de
    trim, LEDs, vibracao e brilho.

Os GUIDs sao deterministicos (uuid5), entao regenerar o arquivo nao muda os IDs.
"""

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pmdg737_common import (  # noqa: E402
    backlight_rpn, powered_rpn, rotor, step_to, switch_var, toggle_to,
)

# --------------------------------------------------------------------------
# Hardware: definicao oficial do MobiFlight (winwing_airbus_throttle_left.joystick.json)
# --------------------------------------------------------------------------
CONTROLLER = {
    # Nome com que o Windows/DirectInput expoe o painel (e o que o MobiFlight mostra)
    "Name": "WINCTRL URSA MINOR 32 Throttle Metal L",
    # Serial do seu painel (GUID mostrado no SimAppPro). Em outro computador o
    # auto-binding do MobiFlight reassocia pelo nome.
    "Serial": "JS-c4381ce0-8065-11f1-8004-444553540000",
}

# Rotulos dos botoes, exatamente como na definicao (Id -> Label).
BUTTON_LABELS = {
    1: "ENGINE MASTER1 ON",
    2: "ENGINE MASTER1 OFF",
    3: "ENGINE MASTER2 ON",
    4: "ENGINE MASTER2 OFF",
    5: "ENGINE FIRE1 Button",
    6: "ENGINE FIRE2 Button",
    7: "ENGINE CRANK MODE",
    8: "ENGINE NORM MODE",
    9: "ENGINE IGN MODE",
    10: "THROTTLE 1 A/THR Button",
    11: "THROTTLE 2 A/THR Button",
    12: "THROTTLE 1 TOGA",
    13: "THROTTLE 1 FLEX",
    14: "THROTTLE 1 CL",
    15: "THROTTLE 1 IDLE",
    16: "THROTTLE 1 REV IDLE",
    17: "THROTTLE 1 FULL REV",
    18: "THROTTLE 2 TOGA",
    19: "THROTTLE 2 FLEX",
    20: "THROTTLE 2 CL",
    21: "THROTTLE 2 IDLE",
    22: "THROTTLE 2 REV IDLE",
    23: "THROTTLE 2 FULL REV",
    24: "ENGINE MODE BUTTON",
    25: "TRIM RESET BUTTON",
    26: "TRIM NOSE L",
    27: "TRIM NOSE NEUTRAL",
    28: "TRIM NOSE R",
    29: "PARKING BRK OFF",
    30: "PARKING BRK ON",
    31: "FLAPS FULL",
    32: "FLAPS 3",
    33: "FLAPS 2",
    34: "FLAPS 1",
    35: "FLAPS 0",
    36: "SPOILERS FULL",
    37: "SPOILERS HALF",
    38: "SPOILERS RET",
    39: "SPOILERS ARMED",
    40: "THROTTLE 1 REVERSE LEVER",
    41: "THROTTLE 2 REVERSE LEVER",
}

# --------------------------------------------------------------------------
# PMDG 737 (SDK PMDG_NG3_SDK.h); convencoes de ROTOR_BRAKE e L:switch em
# ../../pmdg737_common.py
# --------------------------------------------------------------------------
EVT_START_SWITCH = {1: 69751, 2: 69753}   # EVT_OH_LIGHTS_L/R_ENGINE_START (L:switch_119/121_73X)
EVT_START_LEVER = {1: 70320, 2: 70321}    # EVT_CONTROL_STAND_ENG1/2_START_LEVER (L:switch_688/689_73X)
EVT_AT1_DISENGAGE = 70314                 # EVT_CONTROL_STAND_AT1_DISENGAGE_SWITCH
EVT_TOGA2 = 70319                         # EVT_CONTROL_STAND_TOGA2_SWITCH
EVT_FLAPS = {0: 76773, 1: 76774, 2: 76775, 5: 76776, 10: 76777,
             15: 76778, 25: 76779, 30: 76780, 40: 76781}   # EVT_CONTROL_STAND_FLAPS_LEVER_x
EVT_SPEEDBRAKE_DOWN = 76423
EVT_SPEEDBRAKE_ARM = 76424
EVT_RUDDER_TRIM_IND = 70441               # L:switch_809_73X: 0 = todo L, 50 = neutro, 100 = todo R

# Start switch do 737 (valor da L:switch): GRD, OFF, CONT, FLT
SS_GRD, SS_OFF, SS_CONT, SS_FLT = 0, 10, 20, 30

# Detentes de flaps do Ursa Minor -> posicao do 737
FLAPS_MAP = {35: 0, 34: 5, 33: 15, 32: 30, 31: 40}

LCD_PCT = 100
LED_PCT = 100
VIBRATION_MAX_PCT = 40   # vibracao maxima na corrida de solo
WASM_COMMAND_LIMIT = 1000  # bloco de 1024 bytes do MobiFlight, com margem

PROFILE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj",
)

_NS = uuid.UUID("6f1f2b9e-8a4e-4c39-9d0e-737a6f000003")


def guid(key):
    return str(uuid.uuid5(_NS, key))


def start_switches(target):
    """Os dois start switches; labels diferentes porque os dois lacos ficam no mesmo comando."""
    return f"{step_to(EVT_START_SWITCH[1], str(target), label=1)} {step_to(EVT_START_SWITCH[2], str(target), label=2)}"


# --------------------------------------------------------------------------
# Construtores de itens
# --------------------------------------------------------------------------
def rpn_action(code):
    return {"Command": code, "Type": "MSFS2020CustomInputAction"}


def button(btn_id, name, on_press=None, on_release=None, on_hold=None,
           hold_delay=350, repeat_delay=0):
    btn = {}
    if on_press:
        btn["onPress"] = rpn_action(on_press)
    if on_release:
        btn["onRelease"] = rpn_action(on_release)
    if on_hold:
        btn["onHold"] = rpn_action(on_hold)
    btn.update({"LongReleaseDelay": 350, "HoldDelay": hold_delay, "RepeatDelay": repeat_delay})
    return {
        "button": btn,
        "Device": {"Type": "Button", "Name": BUTTON_LABELS[btn_id]},
        "GUID": guid(f"in-{btn_id}"),
        "Active": True,
        "Name": name,
        "Type": "InputConfigItem",
        "Controller": dict(CONTROLLER),
    }


def _source(rpn, key_):
    return {
        "SimConnectValue": {"UUID": guid(f"src-{key_}"), "Value": rpn, "VarType": 2},
        "Type": "SimConnectSource",
    }


def led(pin, name, rpn, test=1.0, pwm=False):
    return {
        "Source": _source(rpn, pin),
        "TestValue": {"type": 1, "Float64": test},
        "Device": {"Name": pin, "Pin": pin, "Brightness": 255, "PwmMode": pwm, "Type": "Output"},
        "DeviceType": "Output",
        "DeviceName": pin,
        "GUID": guid(f"out-{pin}"),
        "Active": True,
        "Name": name,
        "Type": "OutputConfigItem",
        "Controller": dict(CONTROLLER),
    }


def level(pin, name, rpn, test):
    """Saida com valor 0-100 (brilho, vibracao)."""
    return led(pin, name, rpn, test=float(test), pwm=True)


def display(address, name, rpn, test):
    return {
        "Source": _source(rpn, address),
        "TestValue": {"type": 1, "Float64": test},
        "Device": {"Name": address, "Address": address, "Lines": [], "Type": "LcdDisplay"},
        "DeviceType": "LcdDisplay",
        "DeviceName": address,
        "GUID": guid(f"lcd-{address}"),
        "Active": True,
        "Name": name,
        "Type": "OutputConfigItem",
        "Controller": dict(CONTROLLER),
    }


# --------------------------------------------------------------------------
# Entradas (o resto dos botoes e eixos fica no MSFS 2024, veja o README)
# --------------------------------------------------------------------------
inputs = [
    # Start levers: L:switch = 0 em IDLE, 100 em CUTOFF; clica so se precisar
    button(1, "ENG MASTER 1 ON -> start lever 1 IDLE", toggle_to(EVT_START_LEVER[1], want_on=False)),
    button(2, "ENG MASTER 1 OFF -> start lever 1 CUTOFF", toggle_to(EVT_START_LEVER[1], want_on=True)),
    button(3, "ENG MASTER 2 ON -> start lever 2 IDLE", toggle_to(EVT_START_LEVER[2], want_on=False)),
    button(4, "ENG MASTER 2 OFF -> start lever 2 CUTOFF", toggle_to(EVT_START_LEVER[2], want_on=True)),
    # Start switches
    button(5, "ENGINE FIRE 1 -> start switch 1 GRD", step_to(EVT_START_SWITCH[1], str(SS_GRD))),
    button(6, "ENGINE FIRE 2 -> start switch 2 GRD", step_to(EVT_START_SWITCH[2], str(SS_GRD))),
    button(7, "ENG MODE CRANK -> start switches FLT", start_switches(SS_FLT)),
    button(8, "ENG MODE NORM -> start switches OFF", start_switches(SS_OFF)),
    button(9, "ENG MODE IGN -> start switches CONT", start_switches(SS_CONT)),
    # Botoes nas manetes
    button(10, "THROTTLE 1 A/THR -> A/T disengage", rotor(EVT_AT1_DISENGAGE)),
    button(11, "THROTTLE 2 A/THR (segurar) -> TO/GA", on_hold=rotor(EVT_TOGA2)),
    # Speedbrake: o eixo fica no MSFS; ARMED arma e, ao sair do detente, baixa
    button(39, "SPOILERS ARMED -> speedbrake ARM (ao sair: DOWN)",
           rotor(EVT_SPEEDBRAKE_ARM), on_release=rotor(EVT_SPEEDBRAKE_DOWN)),
]
inputs += [
    button(btn_id, f"{BUTTON_LABELS[btn_id]} -> flaps {pos if pos else 'UP'}", rotor(EVT_FLAPS[pos]))
    for btn_id, pos in FLAPS_MAP.items()
]

# --------------------------------------------------------------------------
# Saidas
# --------------------------------------------------------------------------
GROUND_ROLL = (
    f"(A:SIM ON GROUND, Bool) (A:GROUND VELOCITY, knots) 30 > and "
    f"if{{ (A:GROUND VELOCITY, knots) 3 / {VIBRATION_MAX_PCT} min }} els{{ 0 }}"
)

outputs = [
    led("FIRE_1", "LED FIRE 1 - fogo no motor 1", "(A:ENG ON FIRE:1, Bool)"),
    led("FIRE_2", "LED FIRE 2 - fogo no motor 2", "(A:ENG ON FIRE:2, Bool)"),
    led("FAULT_1", "LED FAULT 1 - start switch 1 em GRD", f"{switch_var(EVT_START_SWITCH[1])} {SS_GRD} =="),
    led("FAULT_2", "LED FAULT 2 - start switch 2 em GRD", f"{switch_var(EVT_START_SWITCH[2])} {SS_GRD} =="),
    display("Trim Value", "Rudder trim em unidades (L/R)",
            f"{switch_var(EVT_RUDDER_TRIM_IND)} 50 - 0.34 * 10 * near 10 /", test=-2.5),
    display("Trim Dashes On/Off", "Trim tracejado (nao usado)", "0", test=0.0),
    level("Vibration 1 Percentage", "Vibracao 1 - corrida no solo", GROUND_ROLL, 20),
    level("Vibration 2 Percentage", "Vibracao 2 - corrida no solo", GROUND_ROLL, 20),
    level("Backlight Percentage", "Brilho backlight - dimmer de painel do 737", backlight_rpn(), 50),
    level("LCD Percentage", "Brilho display de trim - com bateria ligada", powered_rpn(LCD_PCT), LCD_PCT),
    level("LED Percentage", "Brilho LEDs - com bateria ligada", powered_rpn(LED_PCT), LED_PCT),
]


def _commands(item):
    """Comandos que o MobiFlight envia ao WASM para este item, com o prefixo."""
    if "button" in item:
        for action in item["button"].values():
            if isinstance(action, dict):
                yield "MF.SimVars.Set." + action["Command"]
    if "Source" in item:
        yield "MF.SimVars.Add." + item["Source"]["SimConnectValue"]["Value"]


project = {
    "Name": "PMDG 737-800 - WINCTRL URSA MINOR 32 Throttle Metal L",
    "ConfigFiles": [
        {
            "Label": "WINCTRL URSA MINOR 32 Throttle Metal L",
            "ReferenceOnly": False,
            "EmbedContent": True,
            "ConfigItems": inputs + outputs,
        }
    ],
    "Sim": "msfs",
    "Features": {"FSUIPC": False, "ProSim": False},
    "_version": "0.10",
}

if __name__ == "__main__":
    for item in inputs + outputs:
        for command in _commands(item):
            assert len(command) <= WASM_COMMAND_LIMIT, (
                f"comando de {len(command)} bytes em '{item['Name']}' excede o limite do MobiFlight"
            )
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(inputs)} entradas, {len(outputs)} saidas -> {os.path.normpath(PROFILE_FILE)}")
