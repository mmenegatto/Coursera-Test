# WINCTRL URSA MINOR 32 Throttle Metal L → PMDG 737-800 (MSFS 2024) — profile MobiFlight

Arquivo: `PMDG_737-800_WINCTRL_URSA_MINOR_32_THROTTLE_L.mfproj`.
O arquivo é gerado por `tools/generate_profile.py`: ajuste as constantes lá e rode o script de novo.

Para usar junto com o AGP e o TCAS, abra `../PMDG_737-800_WINCTRL_COCKPIT.mfproj`, que traz os três painéis no mesmo projeto.

## Requisitos

- MobiFlight Connector **10.x ou superior**, com suporte nativo ao painel (VID 0x4098 / PID 0xB920). O profile espera que ele apareça como **"WINCTRL URSA MINOR 32 Throttle Metal L"**.
- O **SimAppPro da WinWing fechado** enquanto o MobiFlight estiver rodando.
- O módulo WASM do MobiFlight instalado (*Extras → Install WASM Module*).
- **Nenhum eixo do throttle atribuído nos controles do MSFS.** Se as manetes também estiverem configuradas no sim, os dois brigam pelo empuxo.

## Instalação

1. Abra o `.mfproj` pelo MobiFlight (*File → Open*).
2. O auto-binding associa o painel pelo nome. Se aparecer o diálogo *Controller Bindings*, escolha o seu throttle.
3. Clique em **Run** com o 737 carregado.
4. **Calibração:** com o MobiFlight rodando, leve cada manete até IDLE e depois até TOGA (e até FULL REV com a trava de reverso levantada). Enquanto a manete está num desses detentes, o profile grava o valor do eixo e passa a usá-lo. Isso precisa ser feito a cada vez que o sim for aberto; até lá, valem os padrões do gerador.

## Mapeamento — entradas

A primeira coluna usa os nomes exatos dos botões na definição do MobiFlight (`winwing_airbus_throttle_left.joystick.json`).

### Manetes

| Painel | 737-800 |
|---|---|
| Eixo das manetes 1 e 2 (`Axis X` / `Axis Y`) | Empuxo do motor 1 / 2, de IDLE a TOGA (`K:THROTTLEn_AXIS_SET_EX1`, o mesmo evento de um eixo atribuído nos controles do MSFS) |
| Manete abaixo de IDLE com THROTTLE n REVERSE LEVER levantada | Reverso: abre em idle reverse logo abaixo de IDLE e aumenta até o máximo em FULL REV (`K:THROTTLEn_DECR`); ao voltar, recolhe (`K:THROTTLEn_INCR`) |
| THROTTLE n IDLE / TOGA / FULL REV | Calibram o eixo (gravam o valor naquele detente) |
| THROTTLE 1 A/THR Button | A/T disengage |
| THROTTLE 2 A/THR Button | TO/GA |

Sem a trava de reverso levantada, a manete abaixo de IDLE fica em IDLE. Isso evita reverso acidental se a calibração estiver errada. Os detentes FLEX, CL e REV IDLE não têm função, porque o 737 não tem detentes nas manetes.

### Partida dos motores

| Painel | 737-800 |
|---|---|
| ENGINE MASTER1 ON / OFF | Start lever 1 IDLE / CUTOFF |
| ENGINE MASTER2 ON / OFF | Start lever 2 IDLE / CUTOFF |
| ENGINE FIRE1 Button | Start switch 1 em **GRD** |
| ENGINE FIRE2 Button | Start switch 2 em **GRD** |
| ENGINE NORM MODE | Os dois start switches em OFF |
| ENGINE IGN MODE | Os dois start switches em CONT |
| ENGINE CRANK MODE | Os dois start switches em FLT |

Partida típica: seletor em NORM; FIRE2 (start switch 2 em GRD); com N2 em 25 %, MASTER2 ON. Repita com FIRE1 e MASTER1. O start switch volta sozinho para OFF quando o motor de partida desliga.

Os start switches nunca passam por GRD ao trocar entre OFF, CONT e FLT. Só os botões FIRE acionam o motor de partida.

### Flaps, speedbrake, trim e freio

| Painel | 737-800 |
|---|---|
| FLAPS 0 / 1 / 2 / 3 / FULL | Flaps UP / 5 / 15 / 30 / 40 |
| SPOILERS RET | Speedbrake DOWN |
| SPOILERS ARMED | Speedbrake ARM |
| SPOILERS HALF | Speedbrake FLIGHT DETENT |
| SPOILERS FULL | Speedbrake UP |
| TRIM NOSE L / R | Rudder trim esquerda / direita (segurar repete) |
| TRIM RESET BUTTON | Centraliza o rudder trim |
| PARKING BRK ON / OFF | Aplica / solta o parking brake |

O parking brake saiu do AGP: as chaves BRK FAN ficaram livres, e o LED HOT do AGP continua mostrando o parking brake.

### Não mapeado

- ENGINE MODE BUTTON, TRIM NOSE NEUTRAL, THROTTLE n FLEX / CL / REV IDLE: sem equivalente no 737.
- Eixos SLIDER FLAPS e SLIDER SPOILERS: flaps e speedbrake usam os detentes, que são mais precisos.

## Mapeamento — saídas

| Painel | Mostra |
|---|---|
| LED FIRE 1 / 2 | Fogo no motor 1 / 2 |
| LED FAULT 1 / 2 | Motor de partida do motor 1 / 2 acionado (start switch em GRD) |
| Display de trim | Rudder trim em unidades, L/R |
| Vibração 1 / 2 | Corrida no solo acima de 30 kt, proporcional à velocidade (máx. 40 %) |
| Brilho | Fixo: backlight 60 %, LCD 100 %, LED 100 % |

## Se as manetes não derem potência

1. **Run ligado:** o MobiFlight só envia comandos com *Run* ativo e conectado ao sim.
2. **Nenhum eixo do throttle nos controles do MSFS:** um eixo atribuído no sim sobrescreve o que o MobiFlight envia.
3. **Nome dos eixos:** em MobiFlight, abra a entrada "Manete 1" e use o botão de detecção de entrada (*scan*) movendo a manete 1. O dispositivo detectado deve ser `Axis X` (manete 2: `Axis Y`). Se aparecer outro nome, me diga qual que eu ajusto, ou troque `AXIS_THROTTLE` no gerador.
4. **Calibração:** se a potência só começa no meio do curso, leve a manete até IDLE e depois até TOGA para recalibrar.

## Verifique no primeiro voo

1. **Eixos das manetes.** Confira no MobiFlight qual eixo se mexe com cada manete. Se não forem `Axis X` (motor 1) e `Axis Y` (motor 2), troque `AXIS_THROTTLE` no gerador.
2. **Curso do reverso.** O reverso é aberto em `REVERSE_STEPS` passos (20). Se FULL REV não chegar ao reverso máximo, aumente esse valor; se o máximo chegar antes do fim do curso, diminua.
3. **Sentido dos cliques do PMDG** (start levers e start switches). Se MASTER ON levar a alavanca para CUTOFF, ou se o seletor andar ao contrário, inverta `LEFT_CLICK` e `RIGHT_CLICK`.
4. **Rudder trim** via eventos padrão (`K:RUDDER_TRIM_LEFT/RIGHT/SET`). Se o PMDG ignorar, troco pelo knob do PMDG (EVT_FCTL_RUDDER_TRIM).

Depois de qualquer ajuste: `python3 tools/generate_profile.py`, `python3 ../combine_profiles.py` e reabra o profile no MobiFlight.
