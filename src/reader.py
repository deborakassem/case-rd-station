import glob
import json


def read_events(input_dir: str) -> list[dict]:
    """
    Função que lê todos os arquivos JSON do diretório informado.

    Parâmetros
    ----------
    input_dir: str
        Caminho do diretório com os arquivos JSON.

    Retornos
    --------
    list[dict]
        Lista de eventos lidos de todos os arquivos.
    """

    events = []
    
    for filepath in glob.glob(f"{input_dir}/*.json"):
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
                events.extend(data)
            except json.JSONDecodeError as e:
                print(f"Erro ao ler {filepath}: {e}")

    return events

