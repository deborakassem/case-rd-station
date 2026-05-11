from datetime import datetime, timedelta

REQUIRED_FIELDS = ("user_id", "event_type", "timestamp")
VALID_EVENT_TYPES = ("login", "purchase", "logout")


def validate_event(
    event: dict,
    execution_time: datetime
) -> tuple[bool, str]:
    """
    Função que valida um evento de acordo com as regras de negócio pré-definidas.

    Parâmetros
    ----------
    event: dict
        Dicionário com o evento a ser validado.
    execution_time: datetime
        Data e hora de execução da validação.

    Retornos
    --------
    tuple[bool, str]
        (True, "") se válido, (False, "motivo") se inválido.
    """

    # Valida campos obrigatórios
    for field in REQUIRED_FIELDS:
        if field not in event:
            return False, f"Campo obrigatório ausente: {field}"

    # Valida user_id
    if not event["user_id"]:
        return False, "Campo user_id não pode ser vazio."

    # Valida event_type
    if event["event_type"] not in VALID_EVENT_TYPES:
        return False, f"Campo event_type inválido: {event['event_type']}"

    # Valida timestamp
    try:
        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False, f"Campo timestamp inválido: {event['timestamp']}"

    if timestamp > execution_time:
        return False, "Campo timestamp não pode estar no futuro."

    # Valida amount para purchase
    if event["event_type"] == "purchase":
        amount = event.get("amount")
        if amount is None or amount <= 0:
            return False, "Campo amount é obrigatório para purchase e deve ser positivo."

    return True, ""


def filter_event(
    event: dict,
    execution_time: datetime,
    window_days: int
) -> bool:
    """
    Função que verifica se o evento está dentro da janela de tempo esperada.

    Parâmetros
    ----------
    event: dict
        Dicionário com o evento já validado.
    execution_time: datetime
        Data e hora de execução da validação.
    window_days: int
        Número de dias da janela de tempo.

    Retornos
    --------
    bool
        True se dentro da janela, False caso contrário.
    """
    
    timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    window_start = execution_time - timedelta(days=window_days)
    return timestamp >= window_start