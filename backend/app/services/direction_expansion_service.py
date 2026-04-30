from app.schemas.breakthrough import ELEMENT_KEY_TO_TITLE
from app.schemas.direction import (
    ELEMENT_DIRECTION_LIBRARY,
    DirectionExpansionByElement,
    DirectionExpansionResult,
    DirectionSelectionResponse,
    DirectionSuggestion,
)


class DirectionExpansionService:
    def expand(
        self,
        breakthrough_keys: list[str],
    ) -> DirectionExpansionResult:
        elements: list[DirectionExpansionByElement] = []

        for key in breakthrough_keys:
            library_entries = ELEMENT_DIRECTION_LIBRARY.get(key, [])
            suggestions: list[DirectionSuggestion] = []
            for idx, entry in enumerate(library_entries):
                direction_id, title, description, expected_impact, data_needed, related_categories = entry
                suggestions.append(
                    DirectionSuggestion(
                        direction_id=direction_id,
                        element_key=key,
                        title=title,
                        description=description,
                        expected_impact=expected_impact,
                        data_needed=list(data_needed),
                        related_scenario_categories=list(related_categories),
                    )
                )

            elements.append(
                DirectionExpansionByElement(
                    element_key=key,
                    element_title=ELEMENT_KEY_TO_TITLE.get(key, key),
                    suggestions=suggestions,
                )
            )

        total = sum(len(e.suggestions) for e in elements)
        return DirectionExpansionResult(
            generation_mode="rule_based",
            elements=elements,
            total_suggestions=total,
        )

    def resolve_selected_directions(
        self,
        direction_ids: list[str],
    ) -> tuple[list[DirectionSuggestion], list[str]]:
        selected: list[DirectionSuggestion] = []
        all_ids: set[str] = set()

        for element_key, entries in ELEMENT_DIRECTION_LIBRARY.items():
            for entry in entries:
                all_ids.add(entry[0])

        for direction_id in direction_ids:
            for element_key, entries in ELEMENT_DIRECTION_LIBRARY.items():
                for entry in entries:
                    if entry[0] == direction_id:
                        selected.append(
                            DirectionSuggestion(
                                direction_id=direction_id,
                                element_key=element_key,
                                title=entry[1],
                                description=entry[2],
                                expected_impact=entry[3],
                                data_needed=list(entry[4]),
                                related_scenario_categories=list(entry[5]),
                            )
                        )
                        break

        related_categories = list(
            dict.fromkeys(
                category
                for d in selected
                for category in d.related_scenario_categories
            )
        )

        return selected, related_categories

    def build_selection_response(
        self,
        record,
        selected_directions: list[DirectionSuggestion],
    ) -> DirectionSelectionResponse:
        return DirectionSelectionResponse(
            assessment_id=record.assessment_id,
            generation_mode=record.generation_mode,
            selected_directions=selected_directions,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
