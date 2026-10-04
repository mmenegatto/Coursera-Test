# Changelog — profiles WINCTRL para o PMDG 737-800 (MSFS 2024)

## v2.1

**TCAS**
- Seletores comandados com a posição direto no evento do PMDG (`N (>K:#evento)`), método relatado para o 737 do MSFS 2024: seletor de modo (`#70432`), chave XPNDR 1/2 (`#70430`) e o seletor STBY / ON / AUTO do transponder (`#70931`), que agora segue a chave XPDR do painel. Antes, nenhum seletor respondia.

## v2

Ajustes a partir de um profile da comunidade testado no PMDG 737-800 do MSFS 2024.

**Throttle (URSA MINOR 32 Throttle Metal L)**
- Manetes, reverso, eixo do speedbrake, rudder trim e parking brake passam para o MSFS 2024 (tabela no README do throttle). SimAppPro em "Double-stroke four-axle".
- Start levers leem `L:switch_688/689_73X` e só clicam se precisar (antes, dois cliques cegos podiam devolver a alavanca à posição inicial).
- Start switches leem `L:switch_119/121_73X` e giram com a roda do mouse (07/08) só o necessário.
- Speedbrake ARMED: ARM ao entrar no detente, DOWN ao sair; o resto do curso vem do eixo do MSFS.
- TO/GA (TOGA2) só com o botão segurado.
- Display de trim lê `L:switch_809_73X` (±17 unidades).
- LED FAULT reflete o start switch em GRD.
- Serial real do painel no profile.

**AGP e TCAS**
- Autobrake, chave ET e seletor de modo do TCAS leem a posição no PMDG e giram com a roda do mouse (07/08); o TCAS não passa mais por STBY.
- Chave XPNDR 1/2 só clica quando está na posição errada.

**Todos os painéis**
- Brilho: backlight segue o dimmer de painel do 737; displays e LEDs só acendem com a bateria ligada.
- Convenções do PMDG centralizadas em `pmdg737_common.py`.

## v1

Primeira versão dos profiles do AGP, do TCAS e do throttle, e do projeto combinado.
