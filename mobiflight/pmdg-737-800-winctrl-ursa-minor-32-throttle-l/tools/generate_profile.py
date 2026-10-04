#!/usr/bin/env python3
"""
Gera o profile MobiFlight (.mfproj) do WINCTRL URSA MINOR 32 Throttle Metal L
para o PMDG 737-800 (MSFS 2024).

Uso:
    python3 generate_profile.py   # grava ../PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj

Os GUIDs sao deterministicos (uuid5), entao regenerar o arquivo nao muda os IDs.
Todos os valores especificos do PMDG e da calibracao ficam nas constantes
abaixo: se algum precisar de ajuste no seu sim, altere aqui e rode de novo.
"""

import json
import os
import uuid

# --------------------------------------------------------------------------
# Hardware: definicao oficial do MobiFlight (winwing_airbus_throttle_left.joystick.json)
# --------------------------------------------------------------------------
CONTROLLER = {
    # Nome com que o Windows/DirectInput expoe o painel (e o que o MobiFlight mostra)
    "Name": "WINCTRL URSA MINOR 32 Throttle Metal L",
    # Serial "coringa": o auto-binding do MobiFlight associa pelo nome
    # quando ha um unico throttle L conectado.
    "Serial": "JS-00000000-0000-0000-0000-000000000000",
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

# Eixos das manetes: nao estao rotulados na definicao, entao o MobiFlight usa
# o nome DirectInput. Se no seu painel as manetes forem outros eixos (veja no
# MobiFlight qual eixo se mexe), troque aqui.
AXIS_THROTTLE = {1: "Axis X", 2: "Axis Y"}

# --------------------------------------------------------------------------
# Calibracao das manetes (valor bruto do eixo, 0-65535)
# Valores padrao; o profile se recalibra sozinho ao passar pelos detentes
# FULL REV, IDLE e TOGA (grava o valor bruto do eixo naquele momento).
# --------------------------------------------------------------------------
DEFAULT_FULL_REV = 0
DEFAULT_IDLE = 16384
DEFAULT_TOGA = 65535

# Quantos THROTTLEn_DECR levam o reverso do PMDG ao maximo. O primeiro DECR
# (sempre enviado ao entrar na zona de reverso) abre o reverso em idle.
# Se FULL REV nao der reverso total, aumente; se o reverso maximo chegar
# antes do fim do curso, diminua.
REVERSE_STEPS = 20

# --------------------------------------------------------------------------
# PMDG 737 (SDK PMDG_NG3_SDK.h) -> parametro do K:ROTOR_BRAKE
# parametro = (EVENT_ID - 69632) * 100 + acao do mouse
# --------------------------------------------------------------------------
THIRD_PARTY_EVENT_ID_MIN = 69632
LEFT_CLICK = 1   # PMDG: clique esquerdo  (seletor gira anti-horario)
RIGHT_CLICK = 2  # PMDG: clique direito   (seletor gira horario)

EVT_START_SWITCH = {1: 69751, 2: 69753}           # EVT_OH_LIGHTS_L/R_ENGINE_START
EVT_START_LEVER = {1: 70320, 2: 70321}            # EVT_CONTROL_STAND_ENG1/2_START_LEVER
EVT_AT1_DISENGAGE = 70314                          # EVT_CONTROL_STAND_AT1_DISENGAGE_SWITCH
EVT_TOGA1 = 70316                                  # EVT_CONTROL_STAND_TOGA1_SWITCH
EVT_FLAPS = {0: 76773, 1: 76774, 2: 76775, 5: 76776, 10: 76777,
             15: 76778, 25: 76779, 30: 76780, 40: 76781}   # EVT_CONTROL_STAND_FLAPS_LEVER_x
EVT_SPEEDBRAKE_DOWN = 76423
EVT_SPEEDBRAKE_ARM = 76424
EVT_SPEEDBRAKE_FLT_DET = 76426
EVT_SPEEDBRAKE_UP = 76427

# Start switch do 737, da esquerda para a direita
SS_GRD, SS_OFF, SS_CONT, SS_FLT = range(4)
SS_POSITIONS = 4
# Start lever: 0 = CUTOFF, 1 = IDLE
LEVER_CUTOFF, LEVER_IDLE = 0, 1

# Detentes de flaps do Ursa Minor -> posicao do 737
FLAPS_MAP = {35: 0, 34: 5, 33: 15, 32: 30, 31: 40}

# Brilho fixo (0-100 %)
BACKLIGHT_PCT = 60
LCD_PCT = 100
LED_PCT = 100
VIBRATION_MAX_PCT = 40   # vibracao maxima na corrida de solo

PROFILE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj",
)

_NS = uuid.UUID("6f1f2b9e-8a4e-4c39-9d0e-737a6f000003")


def guid(key):
    return str(uuid.uuid5(_NS, key))


def rotor(event_id, action=LEFT_CLICK):
    return f"{(event_id - THIRD_PARTY_EVENT_ID_MIN) * 100 + action} (>K:ROTOR_BRAKE)"


def set_selector(event_id, positions, target):
    """Posicao absoluta sem ler o estado do PMDG: gira ate o batente da
    esquerda e clica para a direita ate o alvo."""
    parts = [rotor(event_id, LEFT_CLICK)] * (positions - 1)
    parts += [rotor(event_id, RIGHT_CLICK)] * target
    return " ".join(parts)


def set_selector_from_right(event_id, positions, target):
    """Mesmo que set_selector, mas partindo do batente da direita. Usado no
    start switch para nunca passar por GRD (que aciona o motor de partida)."""
    parts = [rotor(event_id, RIGHT_CLICK)] * (positions - 1)
    parts += [rotor(event_id, LEFT_CLICK)] * (positions - 1 - target)
    return " ".join(parts)


# --------------------------------------------------------------------------
# Manetes
# O PMDG so aceita empuxo pelos eventos de EIXO (os mesmos de quando um eixo
# e atribuido nos controles do MSFS): THROTTLEn_AXIS_SET_EX1, de -16384
# (idle) a +16384 (maximo). O reverso do PMDG e acionado com THROTTLEn_DECR
# com a manete em idle (cada evento abre mais o reverso) e recolhido com
# THROTTLEn_INCR.
#
# L:vars por motor n:
#   MF_THRn_RAW       ultimo valor bruto do eixo
#   MF_THRn_DET       detente atual: 1 = IDLE, 2 = TOGA, 3 = FULL REV, 0 = fora
#   MF_THRn_IDLE/TOGA/FULLREV  calibracao (valor bruto + 1; 0 = usar padrao)
#   MF_THRn_REVLATCH  1 com a trava de reverso levantada
#   MF_THRn_REVSTEP   quantos THROTTLEn_DECR de reverso ja foram enviados
# --------------------------------------------------------------------------
DET_IDLE, DET_TOGA, DET_FULL_REV = 1, 2, 3


def cal(n, name, default):
    return f"(L:MF_THR{n}_{name}, number) 0 > if{{ (L:MF_THR{n}_{name}, number) 1 - }} els{{ {default} }}"


def _repeat_signed(delta_reg, event_pos, event_neg, steps):
    """Envia event_pos 'delta' vezes se delta > 0, ou event_neg '-delta' vezes
    se delta < 0 (RPN nao tem laco, entao o envio e desenrolado)."""
    parts = [f"{delta_reg} {k} > if{{ (>K:{event_pos}) }}" for k in range(steps)]
    parts += [f"{delta_reg} {-k} < if{{ (>K:{event_neg}) }}" for k in range(steps)]
    return " ".join(parts)


def throttle_axis(n):
    idle = cal(n, "IDLE", DEFAULT_IDLE)
    toga = cal(n, "TOGA", DEFAULT_TOGA)
    full_rev = cal(n, "FULLREV", DEFAULT_FULL_REV)
    revstep = f"(L:MF_THR{n}_REVSTEP, number)"

    # Calibra enquanto a manete esta parada num detente
    calibration = " ".join(
        f"(L:MF_THR{n}_DET, number) {det} == if{{ @ 1 + (>L:MF_THR{n}_{name}, number) }}"
        for det, name in ((DET_IDLE, "IDLE"), (DET_TOGA, "TOGA"), (DET_FULL_REV, "FULLREV"))
    )
    stow_reverse = (
        f"0 {revstep} - s3 {_repeat_signed('l3', f'THROTTLE{n}_DECR', f'THROTTLE{n}_INCR', REVERSE_STEPS)} "
        f"0 (>L:MF_THR{n}_REVSTEP, number)"
    )
    forward = (
        f"{stow_reverse} "
        f"@ {idle} - {toga} {idle} - / 0 max 1 min 32768 * 16384 - flr "
        f"(>K:THROTTLE{n}_AXIS_SET_EX1)"
    )
    reverse = (
        f"-16384 (>K:THROTTLE{n}_AXIS_SET_EX1) "
        f"{idle} @ - {idle} {full_rev} - / 0 max 1 min {REVERSE_STEPS - 1} * near 1 + s2 "
        f"l2 {revstep} - s3 "
        f"{_repeat_signed('l3', f'THROTTLE{n}_DECR', f'THROTTLE{n}_INCR', REVERSE_STEPS)} "
        f"l2 (>L:MF_THR{n}_REVSTEP, number)"
    )
    return (
        f"@ (>L:MF_THR{n}_RAW, number) {calibration} "
        f"@ {idle} < (L:MF_THR{n}_REVLATCH, number) and if{{ {reverse} }} els{{ {forward} }}"
    )


def detent(n, det, name):
    """Botao de detente: marca o detente (para a calibracao no eixo) e ja grava
    o ultimo valor bruto conhecido."""
    return (
        f"{det} (>L:MF_THR{n}_DET, number) "
        f"(L:MF_THR{n}_RAW, number) 1 + (>L:MF_THR{n}_{name}, number)"
    )


def leave_detent(n):
    return f"0 (>L:MF_THR{n}_DET, number)"


def start_switches(target):
    return " ".join(set_selector_from_right(EVT_START_SWITCH[n], SS_POSITIONS, target) for n in (1, 2))


PARK_SET = "(A:BRAKE PARKING POSITION, Bool) ! if{ (>K:PARKING_BRAKES) }"
PARK_RELEASE = "(A:BRAKE PARKING POSITION, Bool) if{ (>K:PARKING_BRAKES) }"


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


def axis(device_name, name, on_change):
    return {
        "analog": {"onChange": rpn_action(on_change)},
        "Device": {"Type": "AnalogInput", "Name": device_name},
        "GUID": guid(f"axis-{device_name}"),
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
# Entradas
# --------------------------------------------------------------------------
inputs = [
    # Partida
    button(1, "ENG MASTER 1 ON -> start lever 1 IDLE",
           set_selector(EVT_START_LEVER[1], 2, LEVER_IDLE)),
    button(2, "ENG MASTER 1 OFF -> start lever 1 CUTOFF",
           set_selector(EVT_START_LEVER[1], 2, LEVER_CUTOFF)),
    button(3, "ENG MASTER 2 ON -> start lever 2 IDLE",
           set_selector(EVT_START_LEVER[2], 2, LEVER_IDLE)),
    button(4, "ENG MASTER 2 OFF -> start lever 2 CUTOFF",
           set_selector(EVT_START_LEVER[2], 2, LEVER_CUTOFF)),
    button(5, "ENGINE FIRE 1 -> start switch 1 GRD",
           set_selector_from_right(EVT_START_SWITCH[1], SS_POSITIONS, SS_GRD)),
    button(6, "ENGINE FIRE 2 -> start switch 2 GRD",
           set_selector_from_right(EVT_START_SWITCH[2], SS_POSITIONS, SS_GRD)),
    button(7, "ENG MODE CRANK -> start switches FLT", start_switches(SS_FLT)),
    button(8, "ENG MODE NORM -> start switches OFF", start_switches(SS_OFF)),
    button(9, "ENG MODE IGN -> start switches CONT", start_switches(SS_CONT)),
    # Botoes nas manetes
    button(10, "THROTTLE 1 A/THR -> A/T disengage", rotor(EVT_AT1_DISENGAGE)),
    button(11, "THROTTLE 2 A/THR -> TO/GA", rotor(EVT_TOGA1)),
    # Detentes usados para calibrar as manetes
    button(12, "THR 1 TOGA -> calibra TOGA", detent(1, DET_TOGA, "TOGA"), on_release=leave_detent(1)),
    button(15, "THR 1 IDLE -> calibra IDLE", detent(1, DET_IDLE, "IDLE"), on_release=leave_detent(1)),
    button(17, "THR 1 FULL REV -> calibra FULL REV", detent(1, DET_FULL_REV, "FULLREV"), on_release=leave_detent(1)),
    button(18, "THR 2 TOGA -> calibra TOGA", detent(2, DET_TOGA, "TOGA"), on_release=leave_detent(2)),
    button(21, "THR 2 IDLE -> calibra IDLE", detent(2, DET_IDLE, "IDLE"), on_release=leave_detent(2)),
    button(23, "THR 2 FULL REV -> calibra FULL REV", detent(2, DET_FULL_REV, "FULLREV"), on_release=leave_detent(2)),
    button(40, "THR 1 REVERSE LEVER -> libera reverso 1",
           "1 (>L:MF_THR1_REVLATCH, number)", on_release="0 (>L:MF_THR1_REVLATCH, number)"),
    button(41, "THR 2 REVERSE LEVER -> libera reverso 2",
           "1 (>L:MF_THR2_REVLATCH, number)", on_release="0 (>L:MF_THR2_REVLATCH, number)"),
    # Trim de leme
    button(25, "TRIM RESET -> centraliza rudder trim", "0 (>K:RUDDER_TRIM_SET)"),
    button(26, "TRIM NOSE L -> rudder trim esquerda (segurar repete)",
           "(>K:RUDDER_TRIM_LEFT)", on_hold="(>K:RUDDER_TRIM_LEFT)", hold_delay=300, repeat_delay=100),
    button(28, "TRIM NOSE R -> rudder trim direita (segurar repete)",
           "(>K:RUDDER_TRIM_RIGHT)", on_hold="(>K:RUDDER_TRIM_RIGHT)", hold_delay=300, repeat_delay=100),
    # Parking brake
    button(29, "PARKING BRK OFF -> solta parking brake", PARK_RELEASE),
    button(30, "PARKING BRK ON -> aplica parking brake", PARK_SET),
    # Speedbrake
    button(38, "SPOILERS RET -> speedbrake DOWN", rotor(EVT_SPEEDBRAKE_DOWN)),
    button(39, "SPOILERS ARMED -> speedbrake ARM", rotor(EVT_SPEEDBRAKE_ARM)),
    button(37, "SPOILERS HALF -> speedbrake FLIGHT DETENT", rotor(EVT_SPEEDBRAKE_FLT_DET)),
    button(36, "SPOILERS FULL -> speedbrake UP", rotor(EVT_SPEEDBRAKE_UP)),
]
inputs += [
    button(btn_id, f"{BUTTON_LABELS[btn_id]} -> flaps {pos if pos else 'UP'}", rotor(EVT_FLAPS[pos]))
    for btn_id, pos in FLAPS_MAP.items()
]
inputs += [
    axis(AXIS_THROTTLE[n], f"Manete {n} -> thrust {n} (com reverso)", throttle_axis(n))
    for n in (1, 2)
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
    led("FAULT_1", "LED FAULT 1 - motor de partida 1 acionado (GRD)", "(A:GENERAL ENG STARTER:1, Bool)"),
    led("FAULT_2", "LED FAULT 2 - motor de partida 2 acionado (GRD)", "(A:GENERAL ENG STARTER:2, Bool)"),
    display("Trim Value", "Rudder trim em unidades (L/R)", "(A:RUDDER TRIM PCT, percent) 0.16 *", test=-2.5),
    display("Trim Dashes On/Off", "Trim tracejado (nao usado)", "0", test=0.0),
    level("Vibration 1 Percentage", "Vibracao 1 - corrida no solo", GROUND_ROLL, 20),
    level("Vibration 2 Percentage", "Vibracao 2 - corrida no solo", GROUND_ROLL, 20),
    level("Backlight Percentage", "Brilho backlight", str(BACKLIGHT_PCT), BACKLIGHT_PCT),
    level("LCD Percentage", "Brilho display de trim", str(LCD_PCT), LCD_PCT),
    level("LED Percentage", "Brilho LEDs", str(LED_PCT), LED_PCT),
]

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
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(inputs)} entradas, {len(outputs)} saidas -> {os.path.normpath(PROFILE_FILE)}")
