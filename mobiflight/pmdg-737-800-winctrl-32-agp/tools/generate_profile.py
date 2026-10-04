#!/usr/bin/env python3
"""
Gera o profile MobiFlight (.mfproj) do WINCTRL 32 AGP Metal para o PMDG 737-800 (MSFS 2024).

Uso:
    python3 generate_profile.py            # grava ../PMDG_737-800_WINCTRL_32_AGP.mfproj

Os GUIDs sao deterministicos (uuid5), entao regenerar o arquivo nao muda os IDs.
Todos os valores especificos do PMDG ficam nas constantes abaixo: se algum
precisar de ajuste no seu sim, altere aqui e rode o script de novo.
"""

import json
import os
import uuid

# --------------------------------------------------------------------------
# Hardware: definicao oficial do MobiFlight (winwing_agp.joystick.json)
# --------------------------------------------------------------------------
CONTROLLER = {
    # Nome com que o Windows/DirectInput expoe o painel (e o que o MobiFlight mostra)
    "Name": "WINCTRL 32 AGP Metal",
    # Serial "coringa": o auto-binding do MobiFlight associa pelo nome
    # quando ha um unico AGP conectado.
    "Serial": "JS-00000000-0000-0000-0000-000000000000",
}

# Rotulos dos botoes, exatamente como em winwing_agp.joystick.json (Id -> Label).
# O profile grava o rotulo como nome do dispositivo de entrada.
BUTTON_LABELS = {
    1: "BRK FAN ON",
    2: "BRK FAN OFF",
    3: "AUTO BRK LO Button",
    4: "AUTO BRK MED Button",
    5: "AUTO BRK MAX Button",
    6: "A/SKID ON",
    7: "A/SKID OFF",
    8: "RST DEC",
    9: "RST Button",
    10: "RST INC",
    11: "CHR DEC",
    12: "CHR Button",
    13: "CHR INC",
    14: "DATE DEC",
    15: "DATE Button",
    16: "DATE INC",
    17: "UTC GPS",
    18: "UTC INT",
    19: "UTC SET",
    20: "ET RUN",
    21: "ET STP",
    22: "ET RST",
    23: "TERR ON ND Button",
    24: "GEAR UP",
    25: "GEAR DOWN",
}

# --------------------------------------------------------------------------
# PMDG 737 (SDK PMDG_NG3_SDK.h) -> parametro do K:ROTOR_BRAKE
# parametro = (EVENT_ID - 69632) * 100 + acao do mouse
# --------------------------------------------------------------------------
THIRD_PARTY_EVENT_ID_MIN = 69632
LEFT_CLICK = 1   # PMDG: clique esquerdo  (seletor gira anti-horario)
RIGHT_CLICK = 2  # PMDG: clique direito   (seletor gira horario)

EVT_MPM_AUTOBRAKE_SELECTOR = 70092
EVT_GEAR_LEVER_OFF = 74183
EVT_EFIS_CPT_TERR = 70007
EVT_CHRONO_L_CHR = 69946
EVT_CHRONO_L_TIME_DATE = 69947
EVT_CHRONO_L_SET = 69948
EVT_CHRONO_L_PLUS = 69949
EVT_CHRONO_L_MINUS = 69950
EVT_CHRONO_L_RESET = 69952
EVT_CHRONO_L_ET = 69953

# L:vars de posicao de chave do PMDG (switch_<offset>_73X), em passos de 10
LVAR_AUTOBRAKE = "L:switch_460_73X"   # 0=RTO 10=OFF 20=1 30=2 40=3 50=MAX
LVAR_CHRONO_L_ET = "L:switch_321_73X"  # 0=RESET 10=HLD 20=RUN
AB_RTO, AB_OFF, AB_1, AB_2, AB_3, AB_MAX = range(6)
ET_RESET, ET_HLD, ET_RUN = range(3)

# Brilho fixo do painel (0-100 %)
BACKLIGHT_PCT = 60
LCD_PCT = 100
LED_PCT = 100

PROFILE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "PMDG_737-800_WINCTRL_32_AGP.mfproj"
)

_NS = uuid.UUID("6f1f2b9e-8a4e-4c39-9d0e-737a6f000001")


def guid(key):
    return str(uuid.uuid5(_NS, key))


def rotor(event_id, action):
    return f"{(event_id - THIRD_PARTY_EVENT_ID_MIN) * 100 + action} (>K:ROTOR_BRAKE)"


def step_selector(lvar, event_id, target_rpn, max_steps=5):
    """RPN que leva um seletor rotativo do PMDG ate o indice alvo, clicando
    a quantidade necessaria de vezes para o lado certo."""
    up = rotor(event_id, RIGHT_CLICK)
    down = rotor(event_id, LEFT_CLICK)
    parts = [f"{target_rpn} ({lvar}, number) 10 / near - s0"]
    for n in range(max_steps):
        parts.append(f"l0 {n} > if{{ {up} }}")
    for n in range(max_steps):
        parts.append(f"l0 {-n} < if{{ {down} }}")
    return " ".join(parts)


def autobrake_toggle(level):
    """Vai para o nivel; se ja estiver nele, volta para OFF (estilo Airbus)."""
    target = f"({LVAR_AUTOBRAKE}, number) 10 / near {level} == if{{ {AB_OFF} }} els{{ {level} }}"
    return step_selector(LVAR_AUTOBRAKE, EVT_MPM_AUTOBRAKE_SELECTOR, target)


# --------------------------------------------------------------------------
# Cronometro / ET espelhados localmente em L:vars do MobiFlight
# (o PMDG nao expoe os valores do relogio)
# state: 0 = zerado, 1 = rodando, 2 = parado
# --------------------------------------------------------------------------
NOW = "(E:ABSOLUTE TIME, seconds)"


def elapsed(prefix):
    return (
        f"(L:{prefix}_STATE, number) 1 == if{{ {NOW} (L:{prefix}_START, number) - }} "
        f"els{{ (L:{prefix}_HELD, number) }}"
    )


CHR_CYCLE = (
    "(L:MF_AGP_CHR_STATE, number) 0 == if{ "
    f"{NOW} (>L:MF_AGP_CHR_START, number) 1 (>L:MF_AGP_CHR_STATE, number) "
    "} els{ (L:MF_AGP_CHR_STATE, number) 1 == if{ "
    f"{NOW} (L:MF_AGP_CHR_START, number) - (>L:MF_AGP_CHR_HELD, number) 2 (>L:MF_AGP_CHR_STATE, number) "
    "} els{ 0 (>L:MF_AGP_CHR_HELD, number) 0 (>L:MF_AGP_CHR_STATE, number) } }"
)
CHR_RESET = "0 (>L:MF_AGP_CHR_HELD, number) 0 (>L:MF_AGP_CHR_STATE, number)"

ET_RUN_LOCAL = (
    "(L:MF_AGP_ET_STATE, number) 1 != if{ "
    f"{NOW} (L:MF_AGP_ET_HELD, number) - (>L:MF_AGP_ET_START, number) 1 (>L:MF_AGP_ET_STATE, number) }}"
)
ET_STOP_LOCAL = (
    "(L:MF_AGP_ET_STATE, number) 1 == if{ "
    f"{NOW} (L:MF_AGP_ET_START, number) - (>L:MF_AGP_ET_HELD, number) 2 (>L:MF_AGP_ET_STATE, number) }}"
)
ET_RESET_LOCAL = "0 (>L:MF_AGP_ET_HELD, number) 0 (>L:MF_AGP_ET_STATE, number)"

# Fonte do display UTC: 0 = GPS (UTC do sim), 1 = INT (hora local do sim), 2 = SET
TIME_SRC = "(L:MF_AGP_UTC_SRC, number) 1 == if{ (E:LOCAL TIME, seconds) } els{ (E:ZULU TIME, seconds) }"
DATE_MODE = "(L:MF_AGP_DATE, number)"


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


def _source(rpn, key):
    return {
        "SimConnectValue": {"UUID": guid(f"src-{key}"), "Value": rpn, "VarType": 2},
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


def brightness(pin, name, pct):
    item = led(pin, name, str(pct), test=float(pct))
    item["Device"]["PwmMode"] = True
    return item


def display(address, name, rpn, test=12.0):
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
# Entradas (25 botoes do AGP)
# --------------------------------------------------------------------------

CLK_PLUS = rotor(EVT_CHRONO_L_PLUS, LEFT_CLICK)
CLK_MINUS = rotor(EVT_CHRONO_L_MINUS, LEFT_CLICK)


def et_select(index):
    return step_selector(LVAR_CHRONO_L_ET, EVT_CHRONO_L_ET, str(index), max_steps=2)


inputs = [
    # Parking brake agora vem do throttle Ursa Minor; BRK FAN fica livre
    button(1, "BRK FAN ON -> (livre)"),
    button(2, "BRK FAN OFF -> (livre)"),
    button(3, "AUTO BRK LO -> Autobrake 1 (toggle OFF) | segurar 1 s = RTO",
           autobrake_toggle(AB_1),
           on_hold=step_selector(LVAR_AUTOBRAKE, EVT_MPM_AUTOBRAKE_SELECTOR, str(AB_RTO)),
           hold_delay=1000),
    button(4, "AUTO BRK MED -> Autobrake 2 (toggle OFF)", autobrake_toggle(AB_2)),
    button(5, "AUTO BRK MAX -> Autobrake 3 (toggle OFF)", autobrake_toggle(AB_3)),
    button(6, "A/SKID ON -> (sem acao, rearma a chave)", None),
    button(7, "A/SKID OFF -> Gear lever OFF", rotor(EVT_GEAR_LEVER_OFF, LEFT_CLICK)),
    button(8, "RST DEC -> Clock CPT MINUS", CLK_MINUS),
    button(9, "RST -> Clock CPT RESET + zera CHR local",
           f"{rotor(EVT_CHRONO_L_RESET, LEFT_CLICK)} {CHR_RESET}"),
    button(10, "RST INC -> Clock CPT PLUS", CLK_PLUS),
    button(11, "CHR DEC -> Clock CPT MINUS", CLK_MINUS),
    button(12, "CHR -> Clock CPT CHR (start/stop/reset) + CHR local",
           f"{rotor(EVT_CHRONO_L_CHR, LEFT_CLICK)} {CHR_CYCLE}"),
    button(13, "CHR INC -> Clock CPT PLUS", CLK_PLUS),
    button(14, "DATE DEC -> Clock CPT MINUS", CLK_MINUS),
    button(15, "DATE -> Clock CPT TIME/DATE + alterna hora/data",
           f"{rotor(EVT_CHRONO_L_TIME_DATE, LEFT_CLICK)} {DATE_MODE} ! (>L:MF_AGP_DATE, number)"),
    button(16, "DATE INC -> Clock CPT PLUS", CLK_PLUS),
    button(17, "UTC GPS -> display mostra UTC do sim", "0 (>L:MF_AGP_UTC_SRC, number)"),
    button(18, "UTC INT -> display mostra hora local do sim", "1 (>L:MF_AGP_UTC_SRC, number)"),
    button(19, "UTC SET -> Clock CPT SET",
           f"2 (>L:MF_AGP_UTC_SRC, number) {rotor(EVT_CHRONO_L_SET, LEFT_CLICK)}"),
    button(20, "ET RUN -> Clock CPT ET RUN + ET local", f"{et_select(ET_RUN)} {ET_RUN_LOCAL}"),
    button(21, "ET STP -> Clock CPT ET HLD + ET local", f"{et_select(ET_HLD)} {ET_STOP_LOCAL}"),
    button(22, "ET RST -> Clock CPT ET RESET + ET local",
           f"{et_select(ET_RESET)} {ET_RESET_LOCAL}",
           on_release=et_select(ET_HLD)),
    button(23, "TERR ON ND -> EFIS CPT TERR",
           f"{rotor(EVT_EFIS_CPT_TERR, LEFT_CLICK)} (L:MF_AGP_TERR, number) ! (>L:MF_AGP_TERR, number)"),
    button(24, "GEAR UP -> Gear lever UP", "(>K:GEAR_UP)"),
    button(25, "GEAR DOWN -> Gear lever DN", "(>K:GEAR_DOWN)"),
]
# --------------------------------------------------------------------------
# Saidas: LEDs
# --------------------------------------------------------------------------
AB_POS = f"({LVAR_AUTOBRAKE}, number) 10 / near"
DECELERATING = (
    "(A:SIM ON GROUND, Bool) (A:GROUND VELOCITY, knots) 20 > and "
    "(A:ACCELERATION BODY Z, feet per second squared) -2 < and"
)


def gear_locked(side):
    return f"(A:GEAR {side} POSITION, percent) 99.5 >"


def gear_transit(side):
    return f"(A:GEAR {side} POSITION, percent) s0 l0 0.5 > l0 99.5 < and"


leds = [
    led("GEAR_1_LOCKED", "LED Gear 1 (L) verde - travado embaixo", gear_locked("LEFT")),
    led("GEAR_2_LOCKED", "LED Gear 2 (NOSE) verde - travado embaixo", gear_locked("CENTER")),
    led("GEAR_3_LOCKED", "LED Gear 3 (R) verde - travado embaixo", gear_locked("RIGHT")),
    led("GEAR_1_UNLOCKED", "LED Gear 1 (L) vermelho - em transito", gear_transit("LEFT")),
    led("GEAR_2_UNLOCKED", "LED Gear 2 (NOSE) vermelho - em transito", gear_transit("CENTER")),
    led("GEAR_3_UNLOCKED", "LED Gear 3 (R) vermelho - em transito", gear_transit("RIGHT")),
    led("GEAR_DOWN_RED_ARROW", "LED seta vermelha - trem em cima, flaps >= 25, < 800 ft RA",
        "(A:GEAR HANDLE POSITION, Bool) ! (A:SIM ON GROUND, Bool) ! and "
        "(A:PLANE ALT ABOVE GROUND, feet) 800 < and (A:FLAPS HANDLE INDEX, number) 6 >= and"),
    led("AUTO_BRK_LO_ON", "LED AUTO BRK LO ON - autobrake 1", f"{AB_POS} {AB_1} =="),
    led("AUTO_BRK_MED_ON", "LED AUTO BRK MED ON - autobrake 2", f"{AB_POS} {AB_2} =="),
    led("AUTO_BRK_MAX_ON", "LED AUTO BRK MAX ON - autobrake 3", f"{AB_POS} {AB_3} =="),
    led("AUTO_BRK_LO_DECEL", "LED AUTO BRK LO DECEL", f"{AB_POS} {AB_1} == {DECELERATING} and"),
    led("AUTO_BRK_MED_DECEL", "LED AUTO BRK MED DECEL", f"{AB_POS} {AB_2} == {DECELERATING} and"),
    led("AUTO_BRK_MAX_DECEL", "LED AUTO BRK MAX DECEL", f"{AB_POS} {AB_3} == {DECELERATING} and"),
    led("BRK_FAN_HOT", "LED BRK FAN HOT - parking brake aplicado", "(A:BRAKE PARKING POSITION, Bool)"),
    led("BRK_FAN_ON", "LED BRK FAN ON - (nao usado no 737)", "0", test=0.0),
    led("TERR_ON_ND_ON", "LED TERR ON ND - estado do TERR no ND do CPT", "(L:MF_AGP_TERR, number)"),
    brightness("Backlight Percentage", "Brilho backlight", BACKLIGHT_PCT),
    brightness("LCD Percentage", "Brilho displays", LCD_PCT),
    brightness("LED Percentage", "Brilho LEDs", LED_PCT),
]

# --------------------------------------------------------------------------
# Saidas: displays do relogio
# --------------------------------------------------------------------------
CHR_S = elapsed("MF_AGP_CHR")
ET_S = elapsed("MF_AGP_ET")

displays = [
    display("UTC HR/MO Value", "UTC hora (ou mes no modo DATE)",
            f"{DATE_MODE} if{{ (E:ZULU MONTH OF YEAR, number) }} els{{ {TIME_SRC} 3600 / flr 24 % }}"),
    display("UTC MIN/DY Value", "UTC minuto (ou dia no modo DATE)",
            f"{DATE_MODE} if{{ (E:ZULU DAY OF MONTH, number) }} els{{ {TIME_SRC} 60 / flr 60 % }}"),
    display("UTC SEC/Y Value", "UTC segundo (ou ano no modo DATE)",
            f"{DATE_MODE} if{{ (E:ZULU YEAR, number) 100 % }} els{{ {TIME_SRC} flr 60 % }}"),
    display("UTC Shown On/Off", "UTC visivel", "1"),
    display("UTC Colon Left Shown On/Off", "UTC ':' esquerdo (oculto no modo DATE)", f"{DATE_MODE} !"),
    display("UTC Colon Right Shown On/Off", "UTC ':' direito (oculto no modo DATE)", f"{DATE_MODE} !"),
    display("CHR MIN Value", "CHR minutos", f"{CHR_S} 60 / flr 100 %"),
    display("CHR SEC Value", "CHR segundos", f"{CHR_S} flr 60 %"),
    display("CHR Shown On/Off", "CHR visivel quando rodando/parado", "(L:MF_AGP_CHR_STATE, number) 0 !="),
    display("CHR Colon Shown On/Off", "CHR ':'", "1"),
    display("ET HR Value", "ET horas", f"{ET_S} 3600 / flr 100 %"),
    display("ET MIN Value", "ET minutos", f"{ET_S} 60 / flr 60 %"),
    display("ET Shown On/Off", "ET visivel quando rodando/parado", "(L:MF_AGP_ET_STATE, number) 0 !="),
    display("ET Colon Shown On/Off", "ET ':'", "1"),
]

project = {
    "Name": "PMDG 737-800 - WINCTRL 32 AGP Metal",
    "ConfigFiles": [
        {
            "Label": "WINCTRL 32 AGP Metal",
            "ReferenceOnly": False,
            "EmbedContent": True,
            "ConfigItems": inputs + leds + displays,
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
    print(f"{len(inputs)} entradas, {len(leds)} LEDs/brilho, {len(displays)} displays -> {os.path.normpath(PROFILE_FILE)}")
