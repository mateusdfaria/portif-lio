"""Testes unitários para o AlertsService."""

from datetime import datetime, timedelta

from services.alerts_service import (
    AlertLevel,
    AlertsService,
    AlertType,
)


def build_historical(days: int, base_rate: float, increment: float = 0.0):
    """Gera dados históricos sintéticos para cenários de tendência."""
    today = datetime.now().date()
    data = []
    for index in range(days):
        date = today - timedelta(days=days - index)
        data.append({"date": date.isoformat(), "occupancy_rate": base_rate + index * increment})
    return data


def test_alert_is_generated_when_threshold_is_exceeded():
    service = AlertsService()

    alerts = service.check_hospital_alerts(
        hospital_id="h1",
        hospital_name="Hospital Teste",
        metrics={"occupancy_rate": 0.95},  # 95% > 85% threshold
    )

    assert any(alert.alert_type == AlertType.OCCUPANCY_HIGH for alert in alerts)
    assert alerts[0].hospital_id == "h1"


def test_trend_alert_is_triggered_with_historical_growth():
    service = AlertsService()
    history = build_historical(days=14, base_rate=0.4, increment=0.01)

    alerts = service.check_hospital_alerts(
        hospital_id="h3",
        hospital_name="Hospital com Tendência",
        metrics={"occupancy_rate": 0.7},
        historical_data=history,
    )

    assert any(alert.alert_type == AlertType.TREND_INCREASING for alert in alerts)


def test_alert_can_be_acknowledged_and_resolved():
    service = AlertsService()
    alert = service.check_hospital_alerts(
        hospital_id="h2",
        hospital_name="Hospital SUS",
        metrics={"icu_occupancy": 0.98},
    )[0]

    assert service.acknowledge_alert(alert.id, "usuario@test.com") is True
    assert service.resolve_alert(alert.id) is True


def test_alert_statistics_return_expected_counts():
    service = AlertsService()
    service.check_hospital_alerts(
        hospital_id="h4",
        hospital_name="Hospital Estatístico",
        metrics={"occupancy_rate": 0.9, "icu_occupancy": 0.97},
    )

    stats = service.get_alert_statistics(days=1)

    assert stats["total_alerts"] == 2
    assert stats["by_level"][AlertLevel.HIGH.value] >= 1


def test_update_alert_rules_allows_custom_thresholds():
    service = AlertsService()
    updated = service.update_alert_rules(
        {AlertType.OCCUPANCY_HIGH.value: {"threshold": 70.0}},
    )
    assert updated is True

    alerts = service.check_hospital_alerts(
        hospital_id="h5",
        hospital_name="Hospital com regra nova",
        metrics={"occupancy_rate": 0.72},
    )

    assert any(alert.alert_type == AlertType.OCCUPANCY_HIGH for alert in alerts)




