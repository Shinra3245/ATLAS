"""El experimento publicado coincide con el entrenamiento de variables coincidentes."""

from __future__ import annotations

from engine.services.ml_info import historical_experiment_info
from ml.training.historical_flood import agreeing_features, holdout_metrics, load_labeled


def test_published_experiment_matches_agreeing_feature_training():
    rows = load_labeled()
    experiment = historical_experiment_info({"riesgo_inundacion_2014": 0}).experiment

    assert [feature["id"] for feature in experiment["features"]] == agreeing_features(rows)
    assert experiment["validation"]["holdouts"] == holdout_metrics(rows)
    assert experiment["validation"]["useful_for_a_decision"] is False
    assert experiment["version"] == "historical-flood-2014-v2"
