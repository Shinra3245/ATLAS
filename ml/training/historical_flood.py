"""Entrenamiento del experimento histórico de inundación 2014.

Usa solo las variables cuyo sentido respecto al daño coincide en Celaya y en
Irapuato. El motor no importa este módulo en cada consulta: publica el
resultado ya medido. Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

CANDIDATE_FEATURES = (
    "altitude_m",
    "dist_rio_arroyo_m",
    "dist_cuerpo_agua_m",
    "dist_canal_m",
    "dist_infra_hidrica_m",
    "dist_camino_m",
    "dist_carretera_m",
    "pobtot",
)
TARGET = "riesgo_inundacion_2014"
MUNICIPALITIES = ("Celaya", "Irapuato")


def default_units_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "processed" / "v1" / "analysis_units.csv"


def load_labeled(path: Path | None = None) -> list[dict[str, str]]:
    source = path or default_units_path()
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row[TARGET] in ("0", "1") and row["municipality"] in MUNICIPALITIES]


def agreeing_features(rows: list[dict[str, str]]) -> list[str]:
    """Variables con el mismo signo de diferencia (daño menos sin daño) en ambos municipios."""

    kept: list[str] = []
    for feature in CANDIDATE_FEATURES:
        signs = []
        for municipality in MUNICIPALITIES:
            damaged = _values(rows, municipality, "1", feature)
            undamaged = _values(rows, municipality, "0", feature)
            signs.append(_mean(damaged) - _mean(undamaged))
        if signs[0] * signs[1] > 0:
            kept.append(feature)
    return kept


def holdout_metrics(rows: list[dict[str, str]] | None = None) -> list[dict[str, float | int | str]]:
    """Entrena en un municipio y prueba en el otro, con peso mayor en la clase con daño."""

    labeled = rows if rows is not None else load_labeled()
    features = agreeing_features(labeled)
    results = []
    for held_out in MUNICIPALITIES:
        train = [row for row in labeled if row["municipality"] != held_out]
        test = [row for row in labeled if row["municipality"] == held_out]
        x_train, y_train = _matrix(train, features)
        x_test, y_test = _matrix(test, features)
        x_train, x_test = _standardize(x_train, x_test)
        beta = _fit_logistic(x_train, y_train)
        predicted = [probability >= 0.5 for probability in _predict(beta, x_test)]
        true_positives = sum(flag and label == 1 for flag, label in zip(predicted, y_test))
        false_positives = sum(flag and label == 0 for flag, label in zip(predicted, y_test))
        false_negatives = sum((not flag) and label == 1 for flag, label in zip(predicted, y_test))
        precision = _ratio(true_positives, true_positives + false_positives)
        recall = _ratio(true_positives, true_positives + false_negatives)
        results.append(
            {
                "held_out": held_out,
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(_f1(precision, recall), 3),
                "true_positives": true_positives,
                "false_positives": false_positives,
            }
        )
    return results


def _values(rows: list[dict[str, str]], municipality: str, label: str, feature: str) -> list[float]:
    return [
        float(row[feature])
        for row in rows
        if row["municipality"] == municipality and row[TARGET] == label
    ]


def _matrix(rows: list[dict[str, str]], features: list[str]) -> tuple[list[list[float]], list[float]]:
    x = [[float(row[feature]) for feature in features] for row in rows]
    y = [float(row[TARGET]) for row in rows]
    return x, y


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _standardize(
    train: list[list[float]], test: list[list[float]]
) -> tuple[list[list[float]], list[list[float]]]:
    width = len(train[0])
    center = [_mean([row[column] for row in train]) for column in range(width)]
    scale = []
    for column, mu in enumerate(center):
        variance = _mean([(row[column] - mu) ** 2 for row in train])
        sigma = variance ** 0.5
        scale.append(sigma if sigma else 1.0)

    def apply(rows: list[list[float]]) -> list[list[float]]:
        return [[(value - center[column]) / scale[column] for column, value in enumerate(row)] for row in rows]

    return apply(train), apply(test)


def _fit_logistic(x: list[list[float]], y: list[float], strength: float = 1.0) -> list[float]:
    """Logística L2. El intercepto no se penaliza. La clase con daño pesa más."""

    count = len(y)
    width = len(x[0])
    positives = max(sum(y), 1.0)
    negatives = max(count - positives, 1.0)
    weights = [count / (2 * positives) if label == 1 else count / (2 * negatives) for label in y]
    beta = [0.0] * (width + 1)
    for _ in range(100):
        probability = _predict(beta, x)
        curvature = [max(weight * p * (1 - p), 1e-8) for weight, p in zip(weights, probability)]
        hessian = [[0.0] * (width + 1) for _ in range(width + 1)]
        gradient = [0.0] * (width + 1)
        for index in range(1, width + 1):
            hessian[index][index] = 1.0
            gradient[index] = beta[index]
        for row, label, weight, p_hat, curve in zip(x, y, weights, probability, curvature):
            design = [1.0, *row]
            residual = weight * (p_hat - label)
            for left, left_value in enumerate(design):
                gradient[left] += strength * left_value * residual
                for right, right_value in enumerate(design):
                    hessian[left][right] += strength * left_value * curve * right_value
        step = _solve(hessian, gradient)
        beta = [value - delta for value, delta in zip(beta, step)]
        if max(abs(delta) for delta in step) < 1e-9:
            break
    return beta


def _predict(beta: list[float], x: list[list[float]]) -> list[float]:
    probabilities = []
    for row in x:
        linear = beta[0] + sum(coef * value for coef, value in zip(beta[1:], row))
        linear = max(-30.0, min(30.0, linear))
        probabilities.append(1 / (1 + math.exp(-linear)))
    return probabilities


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    aug = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(aug[row][column]))
        aug[column], aug[pivot] = aug[pivot], aug[column]
        divisor = aug[column][column]
        for col in range(column, size + 1):
            aug[column][col] /= divisor
        for row in range(size):
            if row == column:
                continue
            factor = aug[row][column]
            for col in range(column, size + 1):
                aug[row][col] -= factor * aug[column][col]
    return [row[size] for row in aug]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)
