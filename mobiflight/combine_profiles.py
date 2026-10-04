#!/usr/bin/env python3
"""
Junta os profiles do AGP e do TCAS num unico projeto MobiFlight, com um
arquivo de configuracao para cada painel. O MobiFlight executa todos os
arquivos de configuracao de um projeto ao mesmo tempo.

Uso:
    python3 combine_profiles.py   # grava PMDG_737-800_WINCTRL_AGP_TCAS.mfproj

Regenere os profiles individuais antes, se tiver alterado algum gerador.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = [
    os.path.join(HERE, "pmdg-737-800-winctrl-32-agp", "PMDG_737-800_WINCTRL_32_AGP.mfproj"),
    os.path.join(HERE, "pmdg-737-800-winctrl-32-tcas", "PMDG_737-800_WINCTRL_32_TCAS.mfproj"),
]
OUTPUT = os.path.join(HERE, "PMDG_737-800_WINCTRL_AGP_TCAS.mfproj")

config_files = []
for path in SOURCES:
    with open(path, encoding="utf-8") as f:
        config_files.extend(json.load(f)["ConfigFiles"])

guids = [item["GUID"] for cf in config_files for item in cf["ConfigItems"]]
assert len(guids) == len(set(guids)), "GUID duplicado entre os profiles"

project = {
    "Name": "PMDG 737-800 - WINCTRL 32 AGP Metal + 32 TCAS",
    "ConfigFiles": config_files,
    "Sim": "msfs",
    "Features": {"FSUIPC": False, "ProSim": False},
    "_version": "0.10",
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(project, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"{len(config_files)} arquivos de configuracao, {len(guids)} itens -> {OUTPUT}")
