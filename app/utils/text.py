from __future__ import annotations


def normalize_text(text: str) -> str:
    # Нормализация для поиска по ключевым словам:
    # - приводим к нижнему регистру
    # - схлопываем пробелы
    # - унифицируем десятичные разделители (',' -> '.')
    normalized = text.lower().strip()
    normalized = normalized.replace(",", ".")
    return " ".join(normalized.split())
