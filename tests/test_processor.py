import unittest
from datetime import datetime, timezone, timedelta

from src.validator import validate_event, filter_event
from src.aggregator import aggregate_events_metrics


class TestValidateEvent(unittest.TestCase):
    """"
    Testes unitários para a função validate_event do módulo validator.py.
    """

    def setUp(self):
        self.execution_time = datetime(2025, 9, 8, tzinfo=timezone.utc)
        self.valid_event = {
            "user_id": "user1",
            "event_type": "login",
            "timestamp": "2025-09-01T10:00:00Z",
            "amount": None
        }

    def test_evento_valido(self):
        is_valid, reason = validate_event(self.valid_event, self.execution_time)
        self.assertTrue(is_valid)
        self.assertEqual(reason, "")

    def test_user_id_vazio(self):
        event = {**self.valid_event, "user_id": ""}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("user_id", reason)

    def test_user_id_nulo(self):
        event = {**self.valid_event, "user_id": None}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("user_id", reason)

    def test_event_type_invalido(self):
        event = {**self.valid_event, "event_type": "unknown"}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("event_type", reason)

    def test_timestamp_no_futuro(self):
        event = {**self.valid_event, "timestamp": "2025-09-09T10:00:00Z"}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("timestamp", reason)

    def test_campo_obrigatorio_ausente_user_id(self):
        event = {"event_type": "login", "timestamp": "2025-09-01T10:00:00Z"}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("user_id", reason)

    def test_campo_obrigatorio_ausente_event_type(self):
        event = {"user_id": "user1", "timestamp": "2025-09-01T10:00:00Z"}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("event_type", reason)

    def test_campo_obrigatorio_ausente_timestamp(self):
        event = {"user_id": "user1", "event_type": "login"}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("timestamp", reason)

    def test_purchase_sem_amount(self):
        event = {**self.valid_event, "event_type": "purchase", "amount": None}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("amount", reason)

    def test_purchase_com_amount_negativo(self):
        event = {**self.valid_event, "event_type": "purchase", "amount": -50.0}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("amount", reason)

    def test_purchase_com_amount_zero(self):
        event = {**self.valid_event, "event_type": "purchase", "amount": 0.0}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertFalse(is_valid)
        self.assertIn("amount", reason)

    def test_purchase_valido(self):
        event = {**self.valid_event, "event_type": "purchase", "amount": 200.0}
        is_valid, reason = validate_event(event, self.execution_time)
        self.assertTrue(is_valid)
        self.assertEqual(reason, "")


class TestFilterEvent(unittest.TestCase):
    """
    Testes unitários para a função filter_event do módulo validator.py.
    """

    def setUp(self):
        self.execution_time = datetime(2025, 9, 8, tzinfo=timezone.utc)
        self.event = {
            "user_id": "user1",
            "event_type": "login",
            "timestamp": "2025-09-01T10:00:00Z",
            "amount": None
        }

    def test_evento_dentro_da_janela(self):
        result = filter_event(self.event, self.execution_time, window_days=30)
        self.assertTrue(result)

    def test_evento_fora_da_janela(self):
        event = {**self.event, "timestamp": "2025-07-01T10:00:00Z"}
        result = filter_event(event, self.execution_time, window_days=30)
        self.assertFalse(result)

    def test_evento_no_limite_da_janela(self):
        event = {**self.event, "timestamp": "2025-08-09T00:00:00Z"}
        result = filter_event(event, self.execution_time, window_days=30)
        self.assertTrue(result)


class TestAggregateEventsMetrics(unittest.TestCase):
    """
    Testes unitários para a função aggregate_events_metrics do módulo aggregator.py.
    """

    def setUp(self):
        self.events = [
            {"user_id": "user1", "event_type": "login", "timestamp": "2025-09-01T10:00:00Z", "amount": None},
            {"user_id": "user2", "event_type": "purchase", "timestamp": "2025-09-01T12:00:00Z", "amount": 200.0},
        ]

    def test_usuarios_unicos(self):
        stats = aggregate_events_metrics(self.events)
        self.assertEqual(stats["unique_users"], 2)

    def test_contagem_de_eventos(self):
        stats = aggregate_events_metrics(self.events)
        self.assertEqual(stats["event_counts"]["login"], 1)
        self.assertEqual(stats["event_counts"]["purchase"], 1)
        self.assertEqual(stats["event_counts"]["logout"], 0)

    def test_total_purchase_amount(self):
        stats = aggregate_events_metrics(self.events)
        self.assertEqual(stats["total_purchase_amount"], 200.0)

    def test_average_purchase_amount(self):
        stats = aggregate_events_metrics(self.events)
        self.assertEqual(stats["average_purchase_amount"], 200.0)

    def test_purchase_by_user(self):
        stats = aggregate_events_metrics(self.events)
        self.assertEqual(stats["purchase_by_user"]["user2"], 200.0)

    def test_lista_vazia(self):
        stats = aggregate_events_metrics([])
        self.assertEqual(stats["unique_users"], 0)
        self.assertEqual(stats["total_purchase_amount"], 0.0)
        self.assertEqual(stats["average_purchase_amount"], 0.0)

    def test_sem_compras(self):
        events = [
            {"user_id": "user1", "event_type": "login", "timestamp": "2025-09-01T10:00:00Z", "amount": None},
        ]
        stats = aggregate_events_metrics(events)
        self.assertEqual(stats["total_purchase_amount"], 0.0)
        self.assertEqual(stats["average_purchase_amount"], 0.0)
        self.assertEqual(stats["purchase_by_user"], {})

    def test_multiplas_compras_mesmo_usuario(self):
        events = [
            {"user_id": "user1", "event_type": "purchase", "timestamp": "2025-09-01T10:00:00Z", "amount": 100.0},
            {"user_id": "user1", "event_type": "purchase", "timestamp": "2025-09-01T11:00:00Z", "amount": 200.0},
        ]
        stats = aggregate_events_metrics(events)
        self.assertEqual(stats["purchase_by_user"]["user1"], 300.0)
        self.assertEqual(stats["average_purchase_amount"], 150.0)


if __name__ == "__main__":
    unittest.main()