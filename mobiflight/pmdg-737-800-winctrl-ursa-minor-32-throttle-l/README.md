# WINCTRL URSA MINOR 32 Throttle Metal L → PMDG 737-800 (MSFS 2024)

Arquivo MobiFlight: `PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj` (gerado por `tools/generate_profile.py`).
Para usar junto com o AGP e o TCAS, abra `../PMDG_737-800_WINCTRL_COCKPIT.mfproj`, que traz os três painéis no mesmo projeto.

## Modelo híbrido

O throttle é configurado em dois lugares, como num profile da comunidade testado no PMDG 737-800 do MSFS 2024:

- **MSFS 2024:** manetes, reverso, eixo do speedbrake, rudder trim e parking brake. São os comandos nativos que o PMDG aceita direto.
- **MobiFlight:** o que é específico do PMDG (start levers, start switches, flaps, speedbrake ARM, A/T disengage, TO/GA), mais o display de trim, os LEDs, a vibração e o brilho.

Não atribua no MSFS os botões que o MobiFlight usa (tabela "MobiFlight" abaixo), e vice-versa.

## 1. SimAppPro

No SimAppPro, em **WINCTRL URSA MINOR 32 Throttle Metal L**, selecione **"Double-stroke four-axle"** e calibre o throttle. Nesse modo, RX/RY cobrem só o empuxo para frente e o reverso sai separado, como o PMDG espera. Depois **feche o SimAppPro**, porque ele disputa o painel com o MobiFlight.

## 2. MSFS 2024: perfil de controles

Crie um perfil de controles para o PMDG 737-800 no dispositivo **WINCTRL URSA MINOR 32 Throttle Metal L** com:

| Comando do MSFS 2024 | Tipo | Entrada do throttle | Opções |
|---|---|---|---|
| THROTTLE 1 AXIS | Eixo | JOYSTICK RAXIS X | Padrão |
| THROTTLE 2 AXIS | Eixo | JOYSTICK RAXIS Y | Padrão |
| THROTTLE 1 DECREASE | Digital | Botões 17 e 23 (FULL REV) | Input Repetition: ON |
| THROTTLE 1 IDLE | Digital | Botões 17 e 23 (FULL REV) | Set Control on Release: ON |
| THROTTLE 2 DECREASE | Digital | Botões 17 e 23 (FULL REV) | Input Repetition: ON |
| THROTTLE 2 IDLE | Digital | Botões 17 e 23 (FULL REV) | Set Control on Release: ON |
| DECREASE THROTTLE | Digital | Botões 40 e 41 (trava de reverso) | Input Repetition: OFF |
| SPOILERS AXIS | Eixo | JOYSTICK SLIDER X | Padrão |
| RUDDER TRIM LEFT | Digital | Botão 26 | Input Repetition: OFF |
| RESET RUDDER TRIM | Digital | Botão 25 | Input Repetition: OFF |
| RUDDER TRIM RIGHT | Digital | Botão 28 | Input Repetition: OFF |
| PARKING BRAKES ON | Digital | Botão 30 | Input Repetition: OFF |
| PARKING BRAKES OFF | Digital | Botão 29 | Input Repetition: OFF |
| TOGGLE PARKING BRAKES | Digital | Botão 30 | Input Repetition: OFF |

O reverso funciona assim: levantar a trava abre o reverso em idle; levar a manete a FULL REV aumenta o reverso enquanto ela estiver lá; sair de FULL REV volta a idle. O reverso atua nos dois motores juntos.

**Parking brake:** no PMDG atual é preciso **segurar o freio (~2 s) antes** de puxar o parking brake; sem isso a alavanca volta para OFF. Use um botão ou tecla com o comando BRAKES enquanto aciona PARKING BRK ON.

O trem de pouso fica na alavanca do AGP, então o botão 24 não é usado.

## 3. MobiFlight

1. Abra o `.mfproj` (*File → Open*) e clique em **Run** com o 737 carregado.
2. O profile já vem com o serial do seu throttle (`JS-c4381ce0-8065-11f1-8004-444553540000`, o GUID mostrado no SimAppPro). Em outro computador, o auto-binding reassocia pelo nome.

| Painel (nome na definição do MobiFlight) | 737-800 |
|---|---|
| ENGINE MASTER1 ON / OFF | Start lever 1 IDLE / CUTOFF |
| ENGINE MASTER2 ON / OFF | Start lever 2 IDLE / CUTOFF |
| ENGINE FIRE1 Button / ENGINE FIRE2 Button | Start switch 1 / 2 em **GRD** |
| ENGINE NORM MODE | Os dois start switches em OFF |
| ENGINE IGN MODE | Os dois start switches em CONT |
| ENGINE CRANK MODE | Os dois start switches em FLT |
| THROTTLE 1 A/THR Button | A/T disengage |
| THROTTLE 2 A/THR Button (segurar) | TO/GA |
| SPOILERS ARMED | Speedbrake ARM; ao sair do detente, DOWN (o eixo do MSFS assume em seguida) |
| FLAPS 0 / 1 / 2 / 3 / FULL | Flaps UP / 5 / 15 / 30 / 40 |

Os start levers e start switches leem a posição atual no PMDG (`L:switch_688/689_73X` e `L:switch_119/121_73X`) e só mexem no que precisa, no mesmo padrão do profile testado. Partida típica: seletor em NORM; FIRE2 (start switch 2 em GRD); com N2 em 25 %, MASTER2 ON. O start switch volta sozinho para OFF quando o motor de partida desliga.

TO/GA só dispara com o botão **segurado** (~0,35 s), para evitar acionamento acidental.

| Saída | Mostra |
|---|---|
| LED FIRE 1 / 2 | Fogo no motor 1 / 2 |
| LED FAULT 1 / 2 | Start switch 1 / 2 em GRD (motor de partida acionado) |
| Display de trim | Rudder trim em unidades, L/R (`L:switch_809_73X`, 50 = neutro, ±17 unidades) |
| Vibração 1 / 2 | Corrida no solo acima de 30 kt, proporcional à velocidade (máx. 40 %) |
| Brilho | Backlight acompanha o dimmer de painel do 737 (`L:BL_MainCA`); display e LEDs acendem só com a bateria ligada |

## Verifique no primeiro voo

1. **Manetes e reverso** pelo MSFS: confira que IDLE dá empuxo mínimo, TOGA o máximo, e que o reverso abre com a trava e aumenta em FULL REV.
2. **LED FIRE** usa a simvar padrão `ENG ON FIRE`. Se não acender no teste de fogo do PMDG, me avise.
3. Se um start switch ou start lever não responder, confira no *Watch Variable* do MobiFlight os valores de `L:switch_119_73X` (0 GRD, 10 OFF, 20 CONT, 30 FLT) e `L:switch_688_73X` (0 IDLE, 100 CUTOFF).

Depois de qualquer ajuste: `python3 tools/generate_profile.py`, `python3 ../combine_profiles.py` e reabra o profile no MobiFlight.
