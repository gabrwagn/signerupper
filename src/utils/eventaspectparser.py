from typing import List, Dict
import utils.date as date


class EventAspectParser:
    VALID_ASPECT_NAMES = [
        "name",
        "date",
        "time",
        "description"
    ]

    VALID_ASPECT_FUNC_VALUE_MAP = {
    }

    @classmethod
    def parse(cls, raw_aspects) -> (Dict, List):
        parsed_aspects = {}
        invalids = []

        for raw_aspect in raw_aspects:
            name_value_pair = raw_aspect.split('=')
            was_parsed = False
            if len(name_value_pair) == 2:
                name = name_value_pair[0].lower()
                value = name_value_pair[1]

                if cls._is_valid_aspect_name(name) and cls._is_valid_aspect_value(name, value):
                    parsed_aspects[name] = value
                    was_parsed = True

            if not was_parsed:
                invalids.append(raw_aspect)

        return parsed_aspects, invalids

    @classmethod
    def _is_valid_aspect_name(cls, name):
        return name in cls.VALID_ASPECT_NAMES

    @classmethod
    def _is_valid_aspect_value(cls, name, value):
        validity_for_value_with_name = {
            "name": lambda n: len(n) > 1,
            "date": date.is_valid_date,
            "time": date.is_valid_time,
            "description": lambda d: True
        }
        return validity_for_value_with_name[name](value)
