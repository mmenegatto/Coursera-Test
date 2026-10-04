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
| XPDR SYS 1 / XPDR SYS 2 | Chave XPNDR 1 / 2 | `0` / `1 (>K:#70430)` |
| XPDR STBY | Transponder **STBY** (e seletor de modo em STBY) | `0 (>K:#70931)` + `#70432` |
| XPDR ON | Transponder **ON** (modo vem das outras chaves) | `1 (>K:#70931)` + `#70432` |
| XPDR AUTO | Transponder **AUTO** (modo vem das outras chaves) | `2 (>K:#70931)` + `#70432` |
| ALT RPTG OFF | Seletor em **ALT RPTG OFF** | `1 (>K:#70432)` |
| ALT RPTG ON | Volta ao modo definido pelo TCAS | `#70432` |
| TCAS STBY | Seletor em **XPNDR** | `2 (>K:#70432)` |
| TCAS TA | Seletor em **TA ONLY** | `3 (>K:#70432)` |
| TCAS TA/RA | Seletor em **TA/RA** | `4 (>K:#70432)` |
| TCAS THRT / ALL / ABV / BLW | **Não mapeado** (não existe no 737) | — |

### Como as três chaves viram o seletor único do 737

O 737 tem um único seletor (STBY / ALT RPTG OFF / XPNDR / TA ONLY / TA/RA), e o painel Airbus tem três chaves. O MobiFlight guarda a posição de cada chave e combina as três:

| XPDR | ALT RPTG | TCAS | Seletor do 737 |
|---|---|---|---|
| STBY | qualquer | qualquer | STBY |
| AUTO ou ON | OFF | qualquer | ALT RPTG OFF |
| AUTO ou ON | ON | STBY | XPNDR |
| AUTO ou ON | ON | TA | TA ONLY |
| AUTO ou ON | ON | TA/RA | TA/RA |

No 737-800 do MSFS 2024, o transponder tem um seletor próprio STBY / ON / AUTO (evento `70931`), comandado direto pela chave XPDR do painel. Em versões do 737 sem esse seletor, o evento é ignorado e o STBY continua vindo do seletor de modo. No início do voo, mexa uma vez em cada uma das três chaves (ou coloque-as na posição desejada) para o MobiFlight registrar a posição física delas.

Os seletores são comandados enviando a posição direto no evento do PMDG (`N (>K:#evento)`), método relatado por usuários do 737 no MSFS 2024. A posição vai direto, sem girar e sem passar por posições intermediárias.

## Mapeamento — saídas

| Painel | Mostra |
|---|---|
| Display de 4 dígitos | O squawk do transponder 1. Durante a digitação, os dígitos aparecem da esquerda para a direita e o resto fica apagado, como no painel real |
| LED ATC FAIL | Transponder em STBY com o avião no ar |
| Brilho | Backlight acompanha o dimmer de painel do 737 (`L:BL_MainCA`); displays e LEDs acendem só com a bateria do 737 ligada (`L:switch_01_73X`) |

## Verifique no primeiro voo

1. **Squawk via `K:XPNDR_SET`.** Se o código digitado não aparecer no painel do PMDG, o 737 está ignorando o evento padrão. Me avise que troco por cliques nos quatro knobs do PMDG (EVT_TCAS_KNOB1 a 4).
2. **Seletores.** Se algum seletor não se mover, abra o log do MobiFlight (nível *Debug*) e confira se aparece `Executing "XPDR …"` / `"TCAS …"` ao mexer na chave. Se aparecer e o 737 não responder, me mande o trecho do log.
3. **Chave XPNDR 1/2.** Se SYS 1 e SYS 2 ficarem trocados, inverta as posições `0` e `1` dos botões 14 e 15 no gerador.

Depois de qualquer ajuste: `python3 tools/generate_profile.py` e reabra o profile no MobiFlight.
