from rest_framework import serializers


def validate_latitude(value):
    if not -90.0 <= value <= 90.0:
        raise serializers.ValidationError(
            "Широта должна находиться в диапазоне [-90.0, 90.0] градусов."
        )
    if count_decimal_digits(value) > 4:
        raise serializers.ValidationError(
            "Широта может иметь до 4 знаков после запятой."
        )
    return value


def validate_longitude(value):
    print(value, "value")
    if not -180.0 <= value <= 180.0:
        raise serializers.ValidationError(
            "Долгота должна находиться в диапазоне [-180.0, 180.0] градусов."
        )
    if count_decimal_digits(value) > 4:
        raise serializers.ValidationError(
            "Долгота может иметь до 4 знаков после запятой."
        )
    return value


def count_decimal_digits(number):
    s = str(number)
    return len(s) - s.find(".") - 1 if "." in s else 0
