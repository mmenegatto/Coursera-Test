#!/usr/bin/env python3
"""
Gera o profile MobiFlight (.mfproj) do WINCTRL 32 TCAS para o PMDG 737-800 (MSFS 2024).

Uso:
    python3 generate_profile.py            # grava ../PMDG_737-800_WINCTRL_32_TCAS.mfproj

Os GUIDs sao deterministicos (uuid5), entao regenerar o arquivo nao muda os IDs.
Todos os valores especificos do PMDG ficam nas constantes abaixo: se algum
precisar de ajuste no seu sim, altere aqui e rode o script de novo.
"""

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pmdg737_common import backlight_rpn, powered_rpn, rotor, step_to, toggle_to  # noqa: E402

# --------------------------------------------------------------------------
# Hardware: definicao oficial do MobiFlight (winwing_tcas.joystick.json)
# --------------------------------------------------------------------------
CONTROLLER = {
    # Nome com que o Windows/DirectInput expoe o painel (e o que o MobiFlight mostra)
    "Name": "WINCTRL 32 TCAS",
    # Serial "coringa": o auto-binding do MobiFlight associa pelo nome
    # quando ha um unico painel TCAS conectado.
    "Serial": "JS-00000000-0000-0000-0000-000000000000",
}

# Rotulos dos botoes, exatamente como em winwing_tcas.joystick.json (Id -> Label).
# O profile grava o rotulo como nome do dispositivo de entrada.
BUTTON_LABELS = {
    1: "Key 1",
    2: "Key 2",
    3: "Key 3",
    4: "Key 4",
    5: "Key 5",
    6: "Key 6",
    7: "Key 7",
    8: "Key 0",
    9: "Key CLR",
    10: "Ident Button",
    11: "XPDR STBY",
    12: "XPDR AUTO",
    13: "XPDR ON",
    14: "XPDR SYS 1",
    15: "XPDR SYS 2",
    16: "ALT RPTG OFF",
    17: "ALT RPTG ON",
    18: "TCAS THRT",
    19: "TCAS ALL",
    20: "TCAS ABV",
    21: "TCAS BLW",
    22: "TCAS STBY",
    23: "TCAS TA",
    24: "TCAS TA/RA",
}

# --------------------------------------------------------------------------
# PMDG 737 (SDK PMDG_NG3_SDK.h); convencoes de ROTOR_BRAKE e L:switch em
# ../../pmdg737_common.py
# --------------------------------------------------------------------------

EVT_TCAS_XPNDR = 70430   # chave XPNDR 1 / 2
EVT_TCAS_MODE = 70432    # seletor de modo
EVT_TCAS_IDENT = 70438   # botao IDENT

# Seletor de modo do 737, da esquerda para a direita (L:switch_800_73X = indice * 10)
MODE_STBY, MODE_ALT_OFF, MODE_XPNDR, MODE_TA_ONLY, MODE_TA_RA = range(5)
# Chave XPNDR: L:switch_798_73X = 0 na posicao 1, diferente de 0 na posicao 2

# Brilho com a bateria do 737 ligada (0-100 %); o backlight segue o dimmer de painel
LCD_PCT = 100
LED_PCT = 100

PROFILE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "PMDG_737-800_WINCTRL_32_TCAS.mfproj"
)

_NS = uuid.UUID("6f1f2b9e-8a4e-4c39-9d0e-737a6f000002")


def guid(key):
    return str(uuid.uuid5(_NS, key))


# --------------------------------------------------------------------------
# Seletor de modo: o 737 tem um unico seletor (STBY / ALT RPTG OFF / XPNDR /
# TA ONLY / TA/RA). As tres chaves do painel Airbus guardam seu estado em
# L:vars e a combinacao define a posicao do seletor do 737.
#   MF_TCAS_XPDR   0 = STBY, 1 = AUTO, 2 = ON
#   MF_TCAS_ALTRPT 0 = OFF,  1 = ON
#   MF_TCAS_MODE   0 = STBY, 1 = TA, 2 = TA/RA
# --------------------------------------------------------------------------
MODE_TARGET = (
    f"(L:MF_TCAS_XPDR, number) 0 == if{{ {MODE_STBY} }} "
    f"els{{ (L:MF_TCAS_ALTRPT, number) 0 == if{{ {MODE_ALT_OFF} }} "
    f"els{{ (L:MF_TCAS_MODE, number) {MODE_XPNDR} + }} }} 10 *"
)
# Le a posicao atual e gira so o necessario, sem passar por STBY
APPLY_MODE = step_to(EVT_TCAS_MODE, MODE_TARGET)


def mode_switch(lvar, value):
    return f"{value} (>L:{lvar}, number) {APPLY_MODE}"


# --------------------------------------------------------------------------
# Teclado: digita o codigo em L:vars e, no 4o digito, envia ao transponder.
#   MF_TCAS_BUF  digitos ja digitados (como numero decimal)
#   MF_TCAS_N    quantidade de digitos digitados (0 = nada em edicao)
# --------------------------------------------------------------------------
SEND_SQUAWK = (
    "(L:MF_TCAS_BUF, number) s1 "
    "l1 1000 / flr 4096 * "
    "l1 100 / flr 10 % 256 * + "
    "l1 10 / flr 10 % 16 * + "
    "l1 10 % + (>K:XPNDR_SET) "
    "0 (>L:MF_TCAS_BUF, number) 0 (>L:MF_TCAS_N, number)"
)


def key(digit):
    return (
        f"(L:MF_TCAS_N, number) 4 < if{{ "
        f"(L:MF_TCAS_BUF, number) 10 * {digit} + (>L:MF_TCAS_BUF, number) "
        f"(L:MF_TCAS_N, number) 1 + (>L:MF_TCAS_N, number) }} "
        f"(L:MF_TCAS_N, number) 4 == if{{ {SEND_SQUAWK} }}"
    )


KEY_CLR = (
    "(L:MF_TCAS_N, number) 0 > if{ "
    "(L:MF_TCAS_BUF, number) 10 / flr (>L:MF_TCAS_BUF, number) "
    "(L:MF_TCAS_N, number) 1 - (>L:MF_TCAS_N, number) }"
)
KEY_CLR_ALL = "0 (>L:MF_TCAS_BUF, number) 0 (>L:MF_TCAS_N, number)"


# --------------------------------------------------------------------------
# Construtores de itens
# --------------------------------------------------------------------------
def rpn_action(code):
    return {"Command": code, "Type": "MSFS2020CustomInputAction"}


def button(btn_id, name, on_press=None, on_release=None, on_hold=None, hold_delay=350):
    btn = {}
    if on_press:
        btn["onPress"] = rpn_action(on_press)
    if on_release:
        btn["onRelease"] = rpn_action(on_release)
    if on_hold:
        btn["onHold"] = rpn_action(on_hold)
    btn.update({"LongReleaseDelay": 350, "HoldDelay": hold_delay, "RepeatDelay": 0})
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


def led(pin, name, rpn, test=1.0):
    return {
        "Source": _source(rpn, pin),
        "TestValue": {"type": 1, "Float64": test},
        "Device": {"Name": pin, "Pin": pin, "Brightness": 255, "PwmMode": False, "Type": "Output"},
        "DeviceType": "Output",
        "DeviceName": pin,
        "GUID": guid(f"out-{pin}"),
        "Active": True,
        "Name": name,
        "Type": "OutputConfigItem",
        "Controller": dict(CONTROLLER),
    }


def brightness(pin, name, rpn, test):
    item = led(pin, name, rpn, test=float(test))
    item["Device"]["PwmMode"] = True
    return item


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
# Entradas (TCAS THRT/ALL/ABV/BLW, ids 18-21, ficam sem mapeamento:
# o 737 nao tem esse seletor)
# --------------------------------------------------------------------------
KEY_IDS = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 0: 8}  # digito -> Id do botao

inputs = [button(btn_id, f"Key {d} -> digita squawk", key(d)) for d, btn_id in KEY_IDS.items()]
inputs += [
    button(9, "Key CLR -> apaga ultimo digito | segurar 1 s = cancela edicao",
           KEY_CLR, on_hold=KEY_CLR_ALL, hold_delay=1000),
    button(10, "Ident Button -> IDENT", rotor(EVT_TCAS_IDENT)),
    button(11, "XPDR STBY -> modo STBY", mode_switch("MF_TCAS_XPDR", 0)),
    button(12, "XPDR AUTO -> transponder ligado", mode_switch("MF_TCAS_XPDR", 1)),
    button(13, "XPDR ON -> transponder ligado", mode_switch("MF_TCAS_XPDR", 2)),
    button(14, "XPDR SYS 1 -> XPNDR 1", toggle_to(EVT_TCAS_XPNDR, want_on=False)),
    button(15, "XPDR SYS 2 -> XPNDR 2", toggle_to(EVT_TCAS_XPNDR, want_on=True)),
    button(16, "ALT RPTG OFF -> modo ALT RPTG OFF", mode_switch("MF_TCAS_ALTRPT", 0)),
    button(17, "ALT RPTG ON -> volta ao modo do TCAS", mode_switch("MF_TCAS_ALTRPT", 1)),
    button(22, "TCAS STBY -> modo XPNDR", mode_switch("MF_TCAS_MODE", 0)),
    button(23, "TCAS TA -> modo TA ONLY", mode_switch("MF_TCAS_MODE", 1)),
    button(24, "TCAS TA/RA -> modo TA/RA", mode_switch("MF_TCAS_MODE", 2)),
]

# --------------------------------------------------------------------------
# Saidas
# --------------------------------------------------------------------------
outputs = [
    display("Number Of Digits", "Digitos visiveis (edicao do squawk)",
            "(L:MF_TCAS_N, number) 0 > if{ (L:MF_TCAS_N, number) } els{ 4 }", test=4.0),
    display("Ident Value", "Squawk (ou digitos em edicao)",
            "(L:MF_TCAS_N, number) 0 > if{ (L:MF_TCAS_BUF, number) } "
            "els{ (A:TRANSPONDER CODE:1, number) }", test=1200.0),
    led("ATC_FAIL", "LED ATC FAIL - transponder em STBY com o aviao no ar",
        "(A:SIM ON GROUND, Bool) ! (L:MF_TCAS_XPDR, number) 0 == and"),
    brightness("Backlight Percentage", "Brilho backlight - dimmer de painel do 737", backlight_rpn(), 50),
    brightness("LCD Percentage", "Brilho display - com bateria ligada", powered_rpn(LCD_PCT), LCD_PCT),
    brightness("LED Percentage", "Brilho LED - com bateria ligada", powered_rpn(LED_PCT), LED_PCT),
]

project = {
    "Name": "PMDG 737-800 - WINCTRL 32 TCAS",
    "ConfigFiles": [
        {
            "Label": "WINCTRL 32 TCAS",
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
