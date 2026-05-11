import argparse
from datetime import datetime, timezone, timedelta

from src.aggregator import aggregate_events
from src.reader import read_events
from src.validator import (
    validate_event,
    filter_event
)
from src.writer import (
    write_stats_csv,
    write_summary_json,
    write_deadletter_json
)


def process_events(
    input_dir: str,
    output_path: str,
    deadletter_path: str,
    window_days: int
) -> None:
    """
    Função que orquestra a pipeline de processador de dados para logs de atividades de usuários.

    Parâmetros
    ----------
    input_dir: str
        Caminho do diretório com os arquivos JSON.
    output_path: str
        Caminho do arquivo de saída stats.csv.
    deadletter_path: str
        Caminho do arquivo de saída deadletter.json.
    window_days: int
        Número de dias da janela de tempo.
    """

    execution_time = datetime.now(timezone.utc)
    # execution_time = datetime(2025, 9, 8, tzinfo=timezone.utc) # teste

    # Leitura dos dados
    all_events = read_events(input_dir=input_dir)

    # Validação dos dados e separação dos eventos válidos e inválidos (deadletter)
    valid_events = []
    deadletter_events = []

    for event in all_events:
        is_valid, reason = validate_event(
            event=event,
            execution_time=execution_time
        )
        if is_valid:
            valid_events.append(event)
        else:
            deadletter_events.append({"raw_event": event, "reason": reason})

    # Filtragem pela janela de tempo
    filtered_events = [
        event for event in valid_events
        if filter_event(
            event=event,
            execution_time=execution_time,
            window_days=window_days
        )
    ]

    # Agregação
    stats = aggregate_events(events=filtered_events)

    # Escrita final
    window = {
        "from": (execution_time - timedelta(days=window_days)).strftime("%Y-%m-%d"),
        "to": execution_time.strftime("%Y-%m-%d"),
    }

    write_stats_csv(
        stats=stats,
        output_path=output_path
    )

    write_summary_json(
        stats=stats,
        window=window,
        deadletter_count=len(deadletter_events),
        output_path=output_path.replace("stats.csv", "summary.json")
    )

    write_deadletter_json(
        deadletter_events=deadletter_events,
        output_path=deadletter_path
    )

    print(f"Processamento concluído.")
    print(f"Eventos lidos: {len(all_events)}")
    print(f"Eventos válidos: {len(valid_events)}")
    print(f"Eventos filtrados: {len(filtered_events)}")
    print(f"Eventos no deadletter: {len(deadletter_events)}")


def main() -> None:
    """"
    Função principal que configura os argumentos de linha de comando e inicia o processamento.
    """

    parser = argparse.ArgumentParser(description="Processador de logs de eventos")
    parser.add_argument("--input-dir", required=True, help="Diretório com os arquivos JSON")
    parser.add_argument("--output", required=True, help="Caminho do arquivo stats.csv")
    parser.add_argument("--deadletter", required=True, help="Caminho do arquivo deadletter.json")
    parser.add_argument("--window-days", type=int, default=30, help="Janela de tempo em dias (padrão: 30)")

    args = parser.parse_args()

    process_events(
        input_dir=args.input_dir,
        output_path=args.output,
        deadletter_path=args.deadletter,
        window_days=args.window_days,
    )


if __name__ == "__main__":
    main()