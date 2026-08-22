"""Camada de conexão com o Microsoft Flight Simulator via SimConnect.

Envolve a biblioteca ``Python-SimConnect`` (pacote ``SimConnect``) para que o
resto do projeto não precise lidar diretamente com detalhes da API nativa.

A importação da biblioteca é adiada (feita dentro dos métodos) porque o
``SimConnect`` só funciona no Windows com o ``SimConnect.dll`` disponível.
Assim é possível importar este módulo em qualquer sistema (ex.: para rodar
testes ou inspecionar o código) sem quebrar imediatamente.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SimConnectionError(RuntimeError):
    """Erro relacionado à conexão/comunicação com o simulador."""


class SimConnection:
    """Gerencia a conexão de baixo nível com o MSFS.

    Expõe helpers para ler variáveis de simulação (SimVars) e disparar
    eventos (comandos). É usada internamente por :class:`MSFSController`,
    mas também pode ser usada diretamente para casos avançados.

    Parameters
    ----------
    request_time_ms:
        Tempo (ms) de validade do cache de leitura de SimVars usado pela
        biblioteca. Valores menores = dados mais "frescos", porém mais
        chamadas ao simulador.
    auto_connect:
        Se ``True`` (padrão), tenta conectar já na construção.
    """

    def __init__(self, request_time_ms: int = 2000, auto_connect: bool = True) -> None:
        self._request_time_ms = request_time_ms
        self._sm: Any = None
        self._requests: Any = None
        self._events: Any = None
        if auto_connect:
            self.connect()

    # ------------------------------------------------------------------ #
    # Ciclo de vida da conexão
    # ------------------------------------------------------------------ #
    def connect(self) -> None:
        """Estabelece a conexão com um MSFS em execução.

        Raises
        ------
        SimConnectionError
            Se a biblioteca não estiver instalada ou o simulador não
            estiver rodando/acessível.
        """
        if self.connected:
            return

        try:
            from SimConnect import SimConnect, AircraftRequests, AircraftEvents
        except ImportError as exc:  # pragma: no cover - depende do ambiente
            raise SimConnectionError(
                "A biblioteca 'SimConnect' não está instalada. "
                "Instale com 'pip install -r requirements.txt' em um "
                "ambiente Windows com o SDK do MSFS."
            ) from exc

        try:
            self._sm = SimConnect()
            self._requests = AircraftRequests(self._sm, _time=self._request_time_ms)
            self._events = AircraftEvents(self._sm)
        except (OSError, ConnectionError, Exception) as exc:  # noqa: BLE001
            # A lib pode lançar exceções variadas quando o sim não está aberto.
            self._sm = None
            raise SimConnectionError(
                "Não foi possível conectar ao MSFS. Verifique se o "
                "simulador está aberto e que uma sessão de voo foi iniciada."
            ) from exc

        logger.info("Conectado ao Microsoft Flight Simulator via SimConnect.")

    def close(self) -> None:
        """Encerra a conexão com o simulador (idempotente)."""
        if self._sm is not None:
            try:
                self._sm.exit()
            except Exception:  # noqa: BLE001 - encerramento best-effort
                logger.debug("Falha ignorada ao encerrar SimConnect.", exc_info=True)
            finally:
                self._sm = None
                self._requests = None
                self._events = None
                logger.info("Conexão com o MSFS encerrada.")

    @property
    def connected(self) -> bool:
        """Retorna ``True`` se há uma conexão ativa."""
        return self._sm is not None

    # ------------------------------------------------------------------ #
    # Leitura / escrita de SimVars e disparo de eventos
    # ------------------------------------------------------------------ #
    def get(self, simvar: str) -> Optional[float]:
        """Lê o valor atual de uma SimVar (ex.: ``"PLANE_ALTITUDE"``)."""
        self._ensure_connected()
        try:
            return self._requests.get(simvar)
        except Exception as exc:  # noqa: BLE001
            raise SimConnectionError(f"Falha ao ler a SimVar '{simvar}'.") from exc

    def set(self, simvar: str, value: float) -> None:
        """Define diretamente o valor de uma SimVar gravável."""
        self._ensure_connected()
        try:
            self._requests.set(simvar, value)
        except Exception as exc:  # noqa: BLE001
            raise SimConnectionError(
                f"Falha ao definir a SimVar '{simvar}' = {value!r}."
            ) from exc

    def trigger(self, event_name: str, value: int = 0) -> None:
        """Dispara um evento/comando do simulador (ex.: ``"GEAR_UP"``).

        Parameters
        ----------
        event_name:
            Nome do evento SimConnect (ver K:Events do SDK do MSFS).
        value:
            Parâmetro opcional do evento (usado por eixos, throttle, etc.).
        """
        self._ensure_connected()
        try:
            event = self._events.find(event_name)
        except Exception as exc:  # noqa: BLE001
            raise SimConnectionError(
                f"Evento '{event_name}' não encontrado no SimConnect."
            ) from exc
        if event is None:
            raise SimConnectionError(f"Evento '{event_name}' não encontrado.")
        try:
            event(value)
        except Exception as exc:  # noqa: BLE001
            raise SimConnectionError(
                f"Falha ao disparar o evento '{event_name}' (value={value})."
            ) from exc
        logger.debug("Evento disparado: %s(%s)", event_name, value)

    # ------------------------------------------------------------------ #
    # Context manager
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "SimConnection":
        if not self.connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # Interno
    # ------------------------------------------------------------------ #
    def _ensure_connected(self) -> None:
        if not self.connected:
            raise SimConnectionError(
                "Sem conexão ativa com o simulador. Chame connect() primeiro."
            )
