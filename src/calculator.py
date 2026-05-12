from src.validator import VALID_EVENT_TYPES


def calculate_events_metrics(events: list[dict]) -> dict:
    """
    Função que calcula as estatísticas dos eventos válidos e filtrados.

    Parâmetros
    ----------
    events: list[dict]
        Lista de eventos válidos e filtrados.

    Retornos
    --------
    dict
        Dicionário com as estatísticas calculadas.
    """

    unique_users = set()  # set garante unicidade dos usuários
    event_counts = {event_type: 0 for event_type in VALID_EVENT_TYPES}
    total_purchase_amount = 0.0
    purchase_by_user = {}

    for event in events:
        unique_users.add(event["user_id"])
        event_counts[event["event_type"]] += 1

        if event["event_type"] == "purchase":
            amount = event["amount"]
            total_purchase_amount += amount
            purchase_by_user[event["user_id"]] = purchase_by_user.get(event["user_id"], 0.0) + amount

    purchase_count = event_counts["purchase"]
    average_purchase_amount = total_purchase_amount / purchase_count if purchase_count > 0 else 0.0

    return {
        "unique_users": len(unique_users),
        "event_counts": event_counts,
        "total_purchase_amount": total_purchase_amount,
        "average_purchase_amount": average_purchase_amount,
        "purchase_by_user": purchase_by_user,
    }