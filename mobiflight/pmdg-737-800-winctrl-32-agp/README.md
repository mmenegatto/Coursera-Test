# WINCTRL 32 AGP Metal → PMDG 737-800 (MSFS 2024) — profile MobiFlight

Arquivo: `PMDG_737-800_WINCTRL_32_AGP.mfproj`.
O arquivo é gerado por `tools/generate_profile.py`: ajuste as constantes lá e rode o script de novo.

## Requisitos

- MobiFlight Connector **10.x ou superior**, com suporte nativo ao "WINWING AGP" (VID 0x4098 / PID 0xBB80). Versões mais antigas não acendem LEDs nem displays.
- O **SimAppPro da WinWing fechado** enquanto o MobiFlight estiver rodando, porque os dois disputam o painel.
- O módulo WASM do MobiFlight instalado (*Extras → Install WASM Module*).
- PMDG 737-800 para MSFS 2024.

## Instalação

1. Copie o `.mfproj` para qualquer pasta e abra pelo MobiFlight (*File → Open*).
2. O profile usa um serial genérico. Com um único AGP conectado, o **auto-binding** associa o painel pelo nome "WINWING AGP". Se aparecer o diálogo *Controller Bindings*, escolha o seu AGP.
3. Clique em **Run** com o 737 carregado.

## Mapeamento — entradas

| AGP | 737-800 | Comando |
|---|---|---|
| GEAR UP | Alavanca do trem UP | `K:GEAR_UP` |
| GEAR DOWN | Alavanca do trem DN | `K:GEAR_DOWN` |
| A/SKID → OFF | Alavanca do trem **OFF** | ROTOR_BRAKE `455101` (EVT_GEAR_LEVER_OFF) |
| A/SKID → ON | sem ação (só rearma a chave) | — |
| BRK FAN ON / OFF | Parking brake aplica / solta | `K:PARKING_BRAKES` condicional ao estado |
| AUTO BRK LO | Autobrake **1** (apertar de novo = OFF) | seletor 460 por passos |
| AUTO BRK LO (segurar 1 s) | Autobrake **RTO** | seletor 460 |
| AUTO BRK MED | Autobrake **2** (apertar de novo = OFF) | seletor 460 |
| AUTO BRK MAX | Autobrake **3** (apertar de novo = OFF) | seletor 460 |
| TERR ON ND | EFIS CPT TERR | `37501` |
| CHR | Relógio CPT CHR (start/stop/reset) + display CHR | `31401` |
| RST | Relógio CPT RESET + zera display CHR | `32001` |
| DATE | Relógio CPT TIME/DATE + alterna hora/data no display | `31501` |
| UTC GPS | Display mostra UTC do sim | — |
| UTC INT | Display mostra hora local do sim | — |
| UTC SET | Relógio CPT SET | `31601` |
| RST / CHR / DATE INC | Relógio CPT + | `31701` |
| RST / CHR / DATE DEC | Relógio CPT − | `31801` |
| ET RUN / STP / RST | Chave ET do relógio CPT RUN / HLD / RESET + display ET | seletor 321 |

Fluxo do trem na decolagem: GEAR UP e depois A/SKID em OFF. No pouso: GEAR DOWN. Volte o A/SKID para ON antes do próximo voo.

O MAX real do autobrake fica no mouse. O seletor de autobrake anda até a posição pedida e para lá, então funciona saindo de qualquer posição.

## Mapeamento — saídas

| AGP | Acende quando |
|---|---|
| Triângulos verdes (1 = L, 2 = NOSE, 3 = R) | Perna do trem travada embaixo (> 99,5 %) |
| UNLK vermelhos | Perna em trânsito |
| Seta vermelha na alavanca | Trem não comandado para baixo, em voo, < 800 ft RA, flaps ≥ 25 |
| AUTO BRK LO / MED / MAX "ON" | Seletor em 1 / 2 / 3 |
| AUTO BRK "DECEL" | Seletor ativo, no solo, > 20 kt e desacelerando |
| BRK FAN HOT | Parking brake aplicado |
| TERR ON ND | TERR ligado no ND (estado guardado pelo MobiFlight) |
| Display UTC | Hora UTC do sim (GPS) ou local (INT); com DATE mostra mês/dia/ano |
| Display CHR | Cronômetro, em sincronia com o botão CHR |
| Display ET | Tempo decorrido, em sincronia com a chave ET |
| Brilho | Fixo: backlight 60 %, LCD 100 %, LED 100 % (constantes no gerador) |

O PMDG não expõe os valores do relógio. Por isso CHR e ET são calculados no próprio MobiFlight, com as L:vars `MF_AGP_*` e o tempo do sim, e disparados pelos mesmos botões que comandam o relógio do 737. Se o relógio do PMDG for mexido pelo mouse, os dois deixam de bater; para realinhar, use RST no CHR ou ET RST.

O mesmo vale para o LED TERR ON ND: o MobiFlight inverte o estado a cada toque. Se o TERR for ligado pelo mouse, aperte o botão duas vezes para realinhar.

## Não mapeado

- Indicador triplo de pressão de freio/acumulador: o MobiFlight não expõe saída para ele.
- "LCD Test On/Off": sem equivalente direto no 737.

## Verifique no primeiro voo

Os IDs de eventos vêm do SDK do PMDG (`PMDG_NG3_SDK.h`) e da lista que vem com o MobiFlight. Algumas convenções do PMDG não pude testar no sim e estão concentradas no topo de `tools/generate_profile.py`:

1. **Sentido do seletor de autobrake.** Se apertar MED levar o seletor para o lado errado, inverta `LEFT_CLICK` e `RIGHT_CLICK`.
2. **L:var de posição do autobrake** (`L:switch_460_73X`, de 0 = RTO a 50 = MAX, em passos de 10). Confira no *Watch Variable* do MobiFlight girando o seletor no cockpit.
3. **Posições da chave ET** (`L:switch_321_73X`, assumido 0 = RESET, 10 = HLD, 20 = RUN).
4. **GEAR_UP / GEAR_DOWN.** Se o PMDG ignorar os eventos padrão, troque por ROTOR_BRAKE `45501` / `45502` (EVT_GEAR_LEVER).

Depois de qualquer ajuste: `python3 tools/generate_profile.py` e reabra o profile no MobiFlight.
