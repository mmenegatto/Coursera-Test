"""
Blocos de RPN comuns aos profiles MobiFlight do PMDG 737 (MSFS 2024).

Convencoes confirmadas num profile testado no sim (PMDG 737-800, MSFS 2024):
  - Eventos do SDK do PMDG via K:ROTOR_BRAKE: (EVENT_ID - 69632) * 100 + acao.
  - A posicao de cada chave fica em L:switch_<offset>_73X. Seletores rotativos
    andam de 10 em 10 por posicao; alavancas de duas posicoes usam 0 e 100.
  - Em seletores rotativos, a acao 07 (roda para cima) aumenta o valor e a 08
    (roda para baixo) diminui.
  - A acao 01 (clique esquerdo) alterna chaves e alavancas de duas posicoes e
    aciona botoes e eventos de posicao direta.
"""

THIRD_PARTY_EVENT_ID_MIN = 69632
CLICK = 1
WHEEL_UP = 7
WHEEL_DOWN = 8

# Bateria ligada e iluminacao de painel do 737 (usadas no brilho dos paineis)
POWER_ON = "(L:switch_01_73X, number) 0 >"
PANEL_LIGHT = "(L:BL_MainCA, number)"


def offset(event_id):
    return event_id - THIRD_PARTY_EVENT_ID_MIN


def rotor(event_id, action=CLICK):
    return f"{offset(event_id) * 100 + action} (>K:ROTOR_BRAKE)"


def switch_var(event_id):
    return f"(L:switch_{offset(event_id)}_73X, number)"


def step_to(event_id, target_rpn, label=1):
    """Leva um seletor rotativo ao valor alvo (em unidades da L:var, 10 por
    posicao), lendo a posicao atual e girando so o necessario. Usa um laco
    RPN (:label ... g<label>), entao o comando fica curto qualquer que seja a
    distancia. Varios step_to no mesmo comando precisam de labels diferentes."""
    up = rotor(event_id, WHEEL_UP)
    down = rotor(event_id, WHEEL_DOWN)
    return (
        f"{target_rpn} {switch_var(event_id)} - 10 div s0 "
        f":{label} "
        f"l0 0 > if{{ {up} l0 -- s0 g{label} }} "
        f"l0 0 < if{{ {down} l0 ++ s0 g{label} }}"
    )


def sweep_to(event_id, positions, target_rpn, label=1):
    """Leva um seletor a um indice (0 = posicao mais a esquerda) sem ler nada
    do PMDG: gira com a roda do mouse ate o batente da esquerda e depois sobe
    'target' posicoes. Funciona qualquer que seja a escala da L:switch do
    painel, ao custo de passar pelas posicoes intermediarias."""
    down = rotor(event_id, WHEEL_DOWN)
    up = rotor(event_id, WHEEL_UP)
    return (
        " ".join([down] * (positions - 1))
        + f" {target_rpn} s0 :{label} l0 0 > if{{ {up} l0 -- s0 g{label} }}"
    )


def set_position(event_id, position_rpn):
    """Coloca um seletor direto numa posicao enviando o evento do PMDG com a
    posicao como parametro (0, 1, 2 ...), sem clique: N (>K:#<event_id>).
    E o metodo relatado por usuarios do 737 no MSFS 2024 para o painel de
    transponder/TCAS."""
    return f"{position_rpn} (>K:#{event_id})"


def toggle_to(event_id, want_on):
    """Chave/alavanca de duas posicoes: clica so se a posicao atual (0 ou nao
    zero) for diferente da desejada."""
    want = 1 if want_on else 0
    return f"{switch_var(event_id)} 0 > {want} != if{{ {rotor(event_id)} }}"


def backlight_rpn():
    """Backlight acompanha o dimmer de painel do 737 (0-100 %)."""
    return f"{PANEL_LIGHT} 50 * 100 min"


def powered_rpn(pct):
    """Displays e LEDs acesos so com a bateria do 737 ligada."""
    return f"{POWER_ON} {pct} *"
