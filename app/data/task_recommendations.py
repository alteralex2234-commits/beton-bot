from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkCategoryRule:
    """
    Правило распознавания задачи и выбора рекомендуемых марок.

    Важно: рекомендуемые марки задаются как названия из `knowledge_base.PRODUCTS`.
    Сам подбор и человеко-читаемое объяснение делается в `ConsultationService`.
    """

    category_key: str
    category_keywords: list[str]
    recommended_product_names: list[str]


# Ключевые категории, которые требуются в сценариях:
# - стяжка → М150 / М200
# - дорожки → М150 / М200
# - фундамент частного дома → М250 / М300
# - ответственные конструкции → М300 / М350
# - водонепроницаемый бетон → W12
# - мелкие работы → пескобетон
#
# Дополнительно:
# - отмостка
# - раствор (как отдельная позиция)
WORK_CATEGORY_RULES: list[WorkCategoryRule] = [
    WorkCategoryRule(
        category_key="stjazhka",
        category_keywords=["стяжка", "стяжки"],
        recommended_product_names=["Бетон В 12,5 (М150)", "Бетон В 15 (М200)"],
    ),
    WorkCategoryRule(
        category_key="dorozhki",
        category_keywords=["дорожки", "дорожка", "тротуар", "плитка", "садовые дорожки"],
        recommended_product_names=["Бетон В 12,5 (М150)", "Бетон В 15 (М200)"],
    ),
    WorkCategoryRule(
        category_key="otmostka",
        category_keywords=["отмостка"],
        recommended_product_names=["Бетон В 12,5 (М150)", "Бетон В 15 (М200)"],
    ),
    WorkCategoryRule(
        category_key="fundament",
        category_keywords=["фундамент", "ленточный", "плита", "плитный"],
        recommended_product_names=["Бетон В 20 (М250)", "Бетон В 22,5 (М300)"],
    ),
    WorkCategoryRule(
        category_key="responsible",
        category_keywords=["монолит", "ответственн", "плита перекрытия", "колонн", "балка", "серьезн", "нагрузк"],
        recommended_product_names=["Бетон В 22,5 (М300)", "Бетон В 25 (М350)"],
    ),
    WorkCategoryRule(
        category_key="private_house",
        category_keywords=["частный дом", "дом", "коттедж", "дача", "индивидуальн"],
        recommended_product_names=["Бетон В 20 (М250)", "Бетон В 22,5 (М300)"],
    ),
    WorkCategoryRule(
        category_key="small_works",
        category_keywords=["мелкие работы", "ремонт", "выравнивание", "небольшие", "небольшой объем", "стяжечк", "наливн", "мелк"],
        recommended_product_names=["Пескобетон В7,5 (М100)", "Пескобетон В15 (М200)"],
    ),
    WorkCategoryRule(
        category_key="mortar",
        category_keywords=["раствор", "кладка", "штукатур"],
        recommended_product_names=["Раствор"],
    ),
]


WATERPROOF_W12_KEYWORDS = [
    "w12",
    "водонепроницаем",
    "водонепроницаемость",
    "гидроизоляц",
    "вода",
    "влажн",
    "грунтовые воды",
    "подвал",
    "подвале",
]


LEAD_CONSENT_KEYWORDS = [
    "оставить заявку",
    "оставьте заявку",
    "заявк",
    "перезвон",
    "связаться",
    "контакт",
    "менеджер",
    "передать номер",
    "передать ваш номер",
    "нужно перезвонить",
    "телефон",
    "номер",
    "позвоните",
]


PRICE_REQUEST_KEYWORDS = [
    "передайте цены",
    "передать цены",
    "прайс",
    "цена",
    "стоимость",
    "сколько стоит",
    "сколько будет",
    "расчет",
    "рассчит",
    "подсч",
    "посчитать",
    "срок",
    "с доставкой",
]


YES_CONFIRM_KEYWORDS = [
    "да",
    "конечно",
    "хочу",
    "хотел",
    "согласен",
    "ок",
    "давай",
    "можно",
    "передавайте",
]


NO_CONFIRM_KEYWORDS = [
    "нет",
    "не нужно",
    "не надо",
    "позже",
    "не сейчас",
    "пока",
    "отложим",
    "не интересно",
]


CONSULTATION_START_KEYWORDS = [
    "нужен бетон",
    "какую марку",
    "марку взять",
    "какую марку взять",
    "нужен бетон",
    "нужен",
    "бетон",
    "пескобетон",
    "раствор",
    "w12",
    "фундамент",
    "стяжка",
    "дорожк",
    "отмостк",
    "дом",
    "ремонт",
]

