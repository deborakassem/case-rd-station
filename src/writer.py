import csv
import json
from datetime import datetime, timezone


def write_stats_csv(
    stats: dict,
    output_path: str
) -> None:
    """
    Função que escreve as estatísticas agregadas em um arquivo CSV.

    Parâmetros
    ----------
    stats: dict
        Dicionário com as estatísticas agregadas.
    output_path: str
        Caminho do arquivo CSV de saída.
    """

    rows = [
        ("unique_users", stats["unique_users"]),
        *[(f"event_{event_type}", count) for event_type, count in stats["event_counts"].items()], # unpacking
        ("total_purchase_amount", stats["total_purchase_amount"]),
        ("average_purchase_amount", stats["average_purchase_amount"]),
        *[(f"purchase_by_user_{user_id}", amount) for user_id, amount in stats["purchase_by_user"].items()] # unpacking
    ]

    # Resultados sobrescritos a cada execução
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"]) # cabeçalho
        writer.writerows(rows)               # registros


def write_summary_json(
    stats: dict,
    window: dict,
    deadletter_count: int,
    output_path: str
) -> None:
    """
    Função que escreve os metadados do processamento em um arquivo JSON.

    Parâmetros
    ----------
    stats: dict
        Dicionário com as estatísticas agregadas.
    window: dict
        Dicionário com as datas de início e fim da janela de tempo.
    deadletter_count: int
        Número de eventos inválidos.
    output_path: str
        Caminho do arquivo de saída.
    """

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), # mantém no formato ISO 8601
        "window": window,
        "stats": {
            "unique_users": stats["unique_users"],
            "events": stats["event_counts"],
            "total_purchase_amount": stats["total_purchase_amount"],
            "average_purchase_amount": stats["average_purchase_amount"],
            "total_purchase_by_user": stats["purchase_by_user"],
        },
        "deadletter_count": deadletter_count,
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def write_deadletter_json(
    deadletter_events: list[dict],
    output_path: str
) -> None:
    """
    Função que escreve os eventos inválidos com cada motivo da rejeição em um arquivo JSON.

    Parâmetros
    ----------
    deadletter_events: list[dict]
        Lista de eventos inválidos com o motivo da rejeição.
    output_path: str
        Caminho do arquivo de saída.
    """

    with open(output_path, "w") as f:
        json.dump(deadletter_events, f, ensure_ascii=False, indent=2)