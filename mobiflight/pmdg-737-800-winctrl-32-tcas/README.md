# WINCTRL 32 TCAS → PMDG 737-800 (MSFS 2024) — profile MobiFlight

Arquivo: `PMDG_737-800_WINCTRL_32_TCAS.mfproj`.
O arquivo é gerado por `tools/generate_profile.py`: ajuste as constantes lá e rode o script de novo.

## Requisitos

- MobiFlight Connector **10.x ou superior**, com suporte nativo ao painel (VID 0x4098 / PID 0xBB81). Ele aparece no MobiFlight como **"WINCTRL 32 TCAS"**.
- O **SimAppPro da WinWing fechado** enquanto o MobiFlight estiver rodando.
- O módulo WASM do MobiFlight instalado (*Extras → Install WASM Module*).
- PMDG 737-800 para MSFS 2024.

## Instalação

1. Abra o `.mfproj` pelo MobiFlight (*File → Open*). Para usar junto com os outros painéis, abra `../PMDG_737-800_WINCTRL_COCKPIT.mfproj`, que já traz AGP, TCAS e throttle no mesmo projeto.
2. O profile usa um serial genérico. Com um único painel TCAS conectado, o **auto-binding** associa pelo nome "WINCTRL 32 TCAS". Se aparecer o diálogo *Controller Bindings*, escolha o seu painel. Sem auto-binding na sua versão, troque o serial `JS-00000000-0000-0000-0000-000000000000` no `.mfproj` pelo serial do seu painel (aparece ao editar qualquer entrada dele no MobiFlight).
3. Clique em **Run** com o 737 carregado.

## Mapeamento — entradas

A primeira coluna usa os nomes exatos dos botões na definição do MobiFlight (`winwing_tcas.joystick.json`).

| Painel | 737-800 | Comando |
|---|---|---|
| Key 0 … Key 7 | Digita o squawk; no 4º dígito envia ao transponder | `K:XPNDR_SET` |
| Key CLR | Apaga o último dígito digitado | — |
| Key CLR (segurar 1 s) | Cancela a edição e volta a mostrar o squawk atual | — |
| Ident Button | IDENT | ROTOR_BRAKE `80601` |
| XPDR SYS 1 / XPDR SYS 2 | Chave XPNDR 1 / 2 (clica só se estiver na posição errada) | ROTOR_BRAKE `79801` |
| XPDR STBY / ON / AUTO | Seletor da **esquerda** do G6992: STBY / ON / AUTO | ROTOR_BRAKE `129907`/`129908` |
| ALT RPTG OFF | Seletor da **direita** em ALT RPTG OFF | ROTOR_BRAKE `80007`/`80008` |
| ALT RPTG ON | Seletor da direita volta ao modo definido pelo TCAS | idem |
| TCAS STBY | Seletor da direita em **XPNDR** | idem |
| TCAS TA | Seletor da direita em **TA ONLY** | idem |
| TCAS TA/RA | Seletor da direita em **TA/RA** | idem |
| TCAS THRT / ALL / ABV / BLW | **Não mapeado** (não existe no 737) | — |

### Painel Gables G6992

O 737-800 do MSFS 2024 usa o transponder Gables G6992, com dois seletores:

- **Esquerda — STBY / ON / AUTO** (evento `70931`): segue a chave XPDR do painel Airbus, posição por posição.
- **Direita — ALT RPTG OFF / XPNDR / TA ONLY / TA/RA** (evento `70432`): combinação das chaves ALT RPTG e TCAS.

| ALT RPTG | TCAS | Seletor da direita |
|---|---|---|
| OFF | qualquer | ALT RPTG OFF |
| ON | STBY | XPNDR |
| ON | TA | TA ONLY |
| ON | TA/RA | TA/RA |

Os dois seletores giram com a roda do mouse (ROTOR_BRAKE 07/08, o mesmo mecanismo que funciona nos outros painéis) até o batente da esquerda e depois avançam até a posição pedida. Isso não depende de ler a posição no PMDG, mas faz o seletor passar pelas posições intermediárias. No início do voo, mexa uma vez em cada chave para o MobiFlight registrar a posição física delas.

A ordem das posições de cada seletor fica nas listas `XPDR_KNOB` e `MODE_KNOB` do gerador.

## Mapeamento — saídas

| Painel | Mostra |
|---|---|
| Display de 4 dígitos | O squawk do transponder 1. Durante a digitação, os dígitos aparecem da esquerda para a direita e o resto fica apagado, como no painel real |
| LED ATC FAIL | Seletor STBY/ON/AUTO em STBY com o avião no ar |
| Brilho | Backlight acompanha o dimmer de painel do 737 (`L:BL_MainCA`); displays e LEDs acendem só com a bateria do 737 ligada (`L:switch_01_73X`) |

## Verifique no primeiro voo

1. **Squawk via `K:XPNDR_SET`.** Se o código digitado não aparecer no painel do PMDG, o 737 está ignorando o evento padrão. Me avise que troco por cliques nos quatro knobs do PMDG (EVT_TCAS_KNOB1 a 4).
2. **Valores de diagnóstico.** O profile traz quatro saídas "DIAGNOSTICO" sem dispositivo, que mostram na coluna de valores do MobiFlight as variáveis dos seletores (`L:switch_1299_73X`, `L:switch_800_73X`, `L:switch_798_73X`) e o estado do transponder no sim. Gire cada seletor no cockpit virtual e anote o valor de cada posição. Se um seletor parar na posição errada, ou se a ordem não for a das listas `XPDR_KNOB`/`MODE_KNOB`, me mande esses valores.
3. **Chave XPNDR 1/2.** Se SYS 1 e SYS 2 ficarem trocados, inverta `want_on` dos botões 14 e 15 no gerador.

Depois de qualquer ajuste: `python3 tools/generate_profile.py` e reabra o profile no MobiFlight.
