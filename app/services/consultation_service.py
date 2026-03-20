from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.data.faq import FAQ_ITEMS
from app.data.knowledge_base import PRODUCTS, ProductKnowledge
from app.data.task_recommendations import (
    CONSULTATION_START_KEYWORDS,
    LEAD_CONSENT_KEYWORDS,
    NO_CONFIRM_KEYWORDS,
    PRICE_REQUEST_KEYWORDS,
    YES_CONFIRM_KEYWORDS,
    WATERPROOF_W12_KEYWORDS,
    WORK_CATEGORY_RULES,
    WorkCategoryRule,
)
from app.utils.text import normalize_text


_VOLUME_RE = re.compile(
    r"(?P<volume>\d+(?:[.,]\d+)?)\s*(?:куб(?:а|ов)?|м3|м\.3|м\s*3)",
    re.IGNORECASE,
)

_DEFAULT_OFFER_TEXT = (
    "Если хотите, я могу передать ваш номер менеджеру — он точно подскажет и рассчитает.\n"
    "Нажмите «Оставить заявку» в меню."
)

_OFFER_BRIEF_TEXT = (
    "Хотите, чтобы менеджер уточнил детали и передал вам точную стоимость/сроки?\n"
    "Нажмите «Оставить заявку»."
)

_OFFER_PRICE_TEXT = (
    "Понял. Чтобы назвать точную цену (с доставкой/самовывозом) и сроки — передам ваш контакт менеджеру.\n"
    "Нажмите «Оставить заявку»."
)

_OFFER_DECLINE_TEXT = (
    "Хорошо. Если позже будет удобно — нажмите «Оставить заявку», и менеджер уточнит детали."
)


@dataclass(frozen=True)
class ConsultationIntent:
    work_category_key: str | None
    desired_product_name: str | None
    is_private_house: bool | None
    waterproof_w12: bool | None
    volume_m3: str | None
    should_start_consultation: bool


@dataclass(frozen=True)
class ConsultationStepResult:
    response_text: str
    next_state: str
    updates: dict[str, Any]


class ConsultationService:
    """
    Сценарный консультант по бетону.

    - не выполняет инженерных расчетов;
    - формулирует рекомендации безопасно: "обычно/часто";
    - ведет диалог через FSM-контекст (что уже узнали).
    """

    # ====== Public: статические тексты ======
    def list_products_text(self) -> str:
        lines = ["Доступные позиции:"]
        for product in PRODUCTS:
            lines.append(f"- {product.name}: {product.short_description}")
        lines.append("")
        lines.append("Если хотите, помогу подобрать вариант под вашу задачу.")
        return "\n".join(lines)

    def list_faq_text(self) -> str:
        lines = ["Частые вопросы:"]
        for question in FAQ_ITEMS:
            lines.append(f"- {question}")
        lines.append("")
        lines.append("Можете нажать на вопрос в меню или написать свой вопрос текстом.")
        return "\n".join(lines)

    # ====== Public: FAQ распознавание ======
    def answer_faq(self, question: str) -> str | None:
        return FAQ_ITEMS.get(question)

    def answer_faq_by_text(self, user_text: str) -> str | None:
        """
        Быстро отвечает на FAQ по ключевым фразам, не включая полный диалог.
        """
        normalized = normalize_text(user_text)
        for question, answer in FAQ_ITEMS.items():
            needle = normalize_text(question.replace("?", ""))
            if needle and needle in normalized:
                return answer
        return None

    # ====== NLP / распознавание ======
    def should_start_consultation(self, user_text: str) -> bool:
        normalized = normalize_text(user_text)
        if not any(k in normalized for k in CONSULTATION_START_KEYWORDS):
            return False
        # Ограничитель: чтобы не запускать диалог на любую фразу "дом" без бетона.
        has_material_word = any(w in normalized for w in ["бетон", "пескобетон", "раствор", "w12"])
        return has_material_word or any(k in normalized for k in ["бетон", "w12", "фундамент", "стяжка", "дорожки", "отмостка"])

    def _parse_volume_m3(self, user_text: str) -> str | None:
        match = _VOLUME_RE.search(user_text)
        if not match:
            return None
        volume = match.group("volume").replace(",", ".")
        return volume

    def _match_product_name(self, user_text: str) -> str | None:
        normalized_text = normalize_text(user_text)
        for product in PRODUCTS:
            for keyword in product.keywords:
                if normalize_text(keyword) in normalized_text:
                    return product.name
        return None

    def _match_work_category(self, user_text: str) -> str | None:
        normalized_text = normalize_text(user_text)

        best: tuple[int, str] | None = None
        for rule in WORK_CATEGORY_RULES:
            score = 0
            for kw in rule.category_keywords:
                # Для некоторых ключей слова в списке могут быть более длинными — используем "in".
                if normalize_text(kw) in normalized_text:
                    score += 1
            if best is None or score > best[0]:
                if score > 0:
                    best = (score, rule.category_key)
        return best[1] if best else None

    def _detect_waterproof_w12(self, user_text: str) -> bool | None:
        normalized = normalize_text(user_text)
        for kw in WATERPROOF_W12_KEYWORDS:
            if normalize_text(kw) in normalized:
                return True
        return None

    def _detect_private_house(self, user_text: str) -> bool | None:
        normalized = normalize_text(user_text)
        # По требованию: "частный дом или другое"
        if "частный дом" in normalized or "коттедж" in normalized or "дача" in normalized or "индивидуальн" in normalized:
            return True
        if "не для частного" in normalized or "не част" in normalized or "коммерц" in normalized:
            return False
        return None

    def determine_intent(self, user_text: str) -> ConsultationIntent:
        normalized = normalize_text(user_text)

        desired_product_name = self._match_product_name(user_text)
        work_category_key = self._match_work_category(user_text)
        waterproof_w12 = self._detect_waterproof_w12(user_text)
        is_private_house = self._detect_private_house(user_text)
        volume_m3 = self._parse_volume_m3(user_text)

        should_start = self.should_start_consultation(user_text)
        # Если явная марка найдена — почти наверняка это запрос на консультацию.
        if desired_product_name:
            should_start = True
        if work_category_key in {"fundament", "otmostka", "stjazhka", "dorozhki", "small_works", "mortar"}:
            should_start = True

        # Нормализуем: если есть ключ "private_house", но в тексте не указано, что это фундамент — оставляем как есть.
        if work_category_key == "private_house":
            is_private_house = True

        # Если есть явный W12, не противоречим категории.
        if "w12" in normalized or "водонепроница" in normalized:
            waterproof_w12 = True

        return ConsultationIntent(
            work_category_key=work_category_key,
            desired_product_name=desired_product_name,
            is_private_house=is_private_house,
            waterproof_w12=waterproof_w12,
            volume_m3=volume_m3,
            should_start_consultation=should_start,
        )

    # ====== Контекст и генерация сценария ======
    def _get_product_by_name(self, product_name: str) -> ProductKnowledge | None:
        for p in PRODUCTS:
            if p.name == product_name:
                return p
        return None

    def _get_rule_by_category(self, category_key: str) -> WorkCategoryRule | None:
        for rule in WORK_CATEGORY_RULES:
            if rule.category_key == category_key:
                return rule
        return None

    def _get_w12_products(self) -> list[ProductKnowledge]:
        return [p for p in PRODUCTS if "W12" in p.name]

    def _should_ask_waterproof(self, fsm_data: dict[str, Any]) -> bool:
        category_key = fsm_data.get("consult_work_category_key")
        if category_key in {"fundament", "otmostka"}:
            return True
        return False

    def _generate_task_question(self, intent: ConsultationIntent, fsm_data: dict[str, Any]) -> str:
        # Если человек уже назвал марку — уточняем назначение.
        if intent.desired_product_name:
            return (
                f"Понял: вы смотрите на «{intent.desired_product_name}».\n"
                "Подскажите, пожалуйста, для чего именно бетон (фундамент/стяжка/дорожки/частный дом/мелкие работы/раствор)?"
            )

        # Первый шаг по требованию.
        return (
            "Подскажите, для чего нужен бетон (чтобы не гадать):\n"
            "фундамент / стяжка / дорожки / отмостка / частный дом / мелкие работы / раствор."
        )

    def _generate_details_question(self, fsm_data: dict[str, Any]) -> str:
        """
        Шаг 2: вопросы уточнения.
        Пытаемся не перегружать, но всегда двигаем диалог к рекомендациям.
        """
        ask_parts: list[str] = []

        if fsm_data.get("consult_volume_m3") is None and not fsm_data.get("asked_volume", False):
            ask_parts.append("какой примерно объем (сколько кубов)?")

        if self._should_ask_waterproof(fsm_data) and fsm_data.get("consult_waterproof_w12") is None and not fsm_data.get("asked_waterproof", False):
            ask_parts.append("есть ли постоянная влажность/вода рядом с основанием (нужен W12)?")

        # Если по логике ничего не нужно — всё равно даем короткий запрос.
        if not ask_parts:
            ask_parts.append("можете подсказать примерный объем, чтобы менеджер точно рассчитал?")

        # Пишем как человек: коротко и по делу.
        return "Отлично, понял. Уточните, пожалуйста: " + " ".join(ask_parts)

    def _recommend_brands(self, fsm_data: dict[str, Any]) -> list[ProductKnowledge]:
        """
        Подбор 1–2 марок на основе категории и флага W12.
        """
        desired_product_name = fsm_data.get("consult_desired_product_name")
        category_key = fsm_data.get("consult_work_category_key")
        waterproof_w12 = fsm_data.get("consult_waterproof_w12")

        if desired_product_name:
            base = self._get_product_by_name(desired_product_name)
            if base:
                # Иногда можно дать второй вариант "рядом", но без навязывания.
                rule = self._get_rule_by_category(category_key) if category_key else None
                if rule:
                    alt = [self._get_product_by_name(n) for n in rule.recommended_product_names]
                    alt_products = [p for p in alt if p and p.name != base.name]
                    return [base] + alt_products[:1]
                return [base]

        # Если нужнее W12 — подменяем кандидаты.
        if waterproof_w12:
            w12_products = self._get_w12_products()
            return w12_products[:2] if w12_products else []

        if not category_key:
            # Фолбэк: обычно берут М150/М200.
            return [self._get_product_by_name("Бетон В 12,5 (М150)"), self._get_product_by_name("Бетон В 15 (М200)")]

        rule = self._get_rule_by_category(category_key)
        if not rule:
            return []

        products = [self._get_product_by_name(name) for name in rule.recommended_product_names]
        return [p for p in products if p]

    def _generate_recommendation_text(self, fsm_data: dict[str, Any], recommendations: list[ProductKnowledge]) -> str:
        """
        Шаг 3–5: рекомендация и безопасная формулировка + дожим.
        """
        if not recommendations:
            return (
                "Чтобы подобрать бетон без ошибок, нужно понять задачу и объем.\n"
                "Если хотите — оставьте заявку, и менеджер уточнит детали и рассчитают вариант."
            )

        # Короткое объяснение без инженерных гарантий.
        category_key = fsm_data.get("consult_work_category_key")
        work_label = category_key if category_key else "ваша задача"

        header = f"По вашей задаче обычно рассматривают следующие варианты для {work_label}:"
        blocks: list[str] = [header]

        for i, product in enumerate(recommendations, start=1):
            blocks.append(
                f"\n{i}) {product.name}\n"
                f"   Обычно используют: {product.typical_usage}\n"
                f"   Заметка для уточнения: {product.consulting_note}"
            )

        blocks.append(
            "\n\nЧтобы не ошибиться, для точного подбора менеджеру важно уточнить детали по объекту "
            "и условиям. Лучше не рассчитывать «вслепую», а согласовать вариант с продавцом/консультантом."
        )
        blocks.append(f"\n\n{_DEFAULT_OFFER_TEXT}")

        return "".join(blocks)

    def _update_fsm_context_from_intent(self, fsm_data: dict[str, Any], intent: ConsultationIntent) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        if intent.work_category_key:
            updates["consult_work_category_key"] = intent.work_category_key
        if intent.desired_product_name:
            updates["consult_desired_product_name"] = intent.desired_product_name
        if intent.is_private_house is not None:
            updates["consult_is_private_house"] = intent.is_private_house
        if intent.waterproof_w12 is not None:
            updates["consult_waterproof_w12"] = intent.waterproof_w12
            updates["asked_waterproof"] = True
        if intent.volume_m3 is not None:
            updates["consult_volume_m3"] = intent.volume_m3
            updates["asked_volume"] = True
        return updates

    # ====== FSM step handlers (логика) ======
    async def task_step(self, user_text: str, fsm_data: dict[str, Any]) -> ConsultationStepResult:
        intent = self.determine_intent(user_text)
        updates = self._update_fsm_context_from_intent(fsm_data, intent)
        merged = {**fsm_data, **updates}

        # Шаг 1: если задача не определена — просим назначение.
        category_key = merged.get("consult_work_category_key")
        if category_key is None and merged.get("consult_desired_product_name") is None:
            return ConsultationStepResult(
                response_text=self._generate_task_question(intent, merged),
                next_state="task",
                updates=updates,
            )

        # Если речь о фундаменте, можно уточнить "частный дом или другое".
        if category_key in {"fundament"} and merged.get("consult_is_private_house") is None and not merged.get("asked_private_house", False):
            updates["asked_private_house"] = True
            return ConsultationStepResult(
                response_text="Уточните, пожалуйста: это частный дом или другой объект?",
                next_state="task",
                updates=updates,
            )

        # Переходим к шагу 2 и задаем недостающие детали.
        question = self._generate_details_question(merged)
        return ConsultationStepResult(
            response_text=question,
            next_state="details",
            updates=updates,
        )

    async def details_step(self, user_text: str, fsm_data: dict[str, Any]) -> ConsultationStepResult:
        intent = self.determine_intent(user_text)
        updates = self._update_fsm_context_from_intent(fsm_data, intent)
        merged = {**fsm_data, **updates}

        # Если в шаге деталей пользователь задал FAQ — вернем ответ и оставим состояние.
        # (FAQ-распознавание делается снаружи в handlers, но оставляем защиту.)
        faq_answer = self.answer_faq_by_text(user_text)
        if faq_answer:
            return ConsultationStepResult(
                response_text=faq_answer,
                next_state="details",
                updates=updates,
            )

        # Шаг 2 (докрутка): volume
        if merged.get("consult_volume_m3") is None and not merged.get("asked_volume", False):
            updates["asked_volume"] = True
            return ConsultationStepResult(
                response_text="Какой примерно объем вам нужен (сколько кубов)?",
                next_state="details",
                updates=updates,
            )

        # Шаг 2 (докрутка): W12
        if self._should_ask_waterproof(merged) and merged.get("consult_waterproof_w12") is None and not merged.get("asked_waterproof", False):
            updates["asked_waterproof"] = True
            return ConsultationStepResult(
                response_text="Важно, чтобы бетон был водонепроницаемым (W12)? Скажете, есть ли постоянная влажность/вода рядом с основанием?",
                next_state="details",
                updates=updates,
            )

        # Шаг 3: рекомендация + дожим
        recommendations = self._recommend_brands(merged)
        response = self._generate_recommendation_text(merged, recommendations)
        return ConsultationStepResult(
            response_text=response,
            next_state="offer",
            updates=updates,
        )

    async def offer_step(self, user_text: str, fsm_data: dict[str, Any]) -> ConsultationStepResult:
        """
        Шаг 5: короткий текст, распознаем согласие на лид и отдельно обрабатываем запрос «передайте цены».
        """
        faq_answer = self.answer_faq_by_text(user_text)
        if faq_answer:
            return ConsultationStepResult(
                response_text=faq_answer,
                next_state="offer",
                updates={},
            )

        normalized = normalize_text(user_text)

        # Контекстные признаки.
        price_requested = bool(fsm_data.get("offer_price_requested", False))

        wants_lead = any(k in normalized for k in LEAD_CONSENT_KEYWORDS)
        wants_prices = any(k in normalized for k in PRICE_REQUEST_KEYWORDS)
        is_negative = any(k in normalized for k in NO_CONFIRM_KEYWORDS)
        is_yes = any(k in normalized for k in YES_CONFIRM_KEYWORDS)

        # Сначала — явное согласие на лид.
        if wants_lead:
            intent = self.determine_intent(user_text)
            updates = self._update_fsm_context_from_intent(fsm_data, intent)
            return ConsultationStepResult(
                response_text="Хорошо, сейчас соберу данные для заявки.",
                next_state="offer",
                updates=updates | {"wants_lead": True, "offer_price_requested": False},
            )

        # Затем — запрос на цены/расчет.
        if wants_prices:
            return ConsultationStepResult(
                response_text=_OFFER_PRICE_TEXT,
                next_state="offer",
                updates={"offer_price_requested": True},
            )

        # Если ранее просили «цены», а теперь человек подтвердил — считаем согласие.
        if price_requested and is_yes:
            intent = self.determine_intent(user_text)
            updates = self._update_fsm_context_from_intent(fsm_data, intent)
            return ConsultationStepResult(
                response_text="Отлично, сейчас соберу данные для заявки.",
                next_state="offer",
                updates=updates | {"wants_lead": True, "offer_price_requested": False},
            )

        # Если человек отказывается — не дожимаем, но оставляем дверь открытой.
        if is_negative:
            return ConsultationStepResult(
                response_text=_OFFER_DECLINE_TEXT,
                next_state="offer",
                updates={"offer_price_requested": False},
            )

        # Иначе — короткий текст без повторения длинной рекомендации.
        return ConsultationStepResult(
            response_text=_OFFER_BRIEF_TEXT,
            next_state="offer",
            updates={"offer_price_requested": price_requested},
        )

