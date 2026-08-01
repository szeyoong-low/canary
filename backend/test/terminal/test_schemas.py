from typing import Annotated, Any

import pytest
from pydantic import AfterValidator, BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo

from src.global_types import Params
from src.terminal.schemas import _optional_fields
from src.validators.primitives import ParamBaseModel


def _reject_non_positive(n: int) -> int:
    if n > 0:
        return n
    raise ValueError(f"{n} must be a positive integer")


# This type alias keeps the validator inside the alias, so after the
# required -> optional rewrite it lives in the non-None branch of the union
# rather than at field level, and an explicit None (default value) skips it.
# Inlining a bare Annotated instead would hoist the validator to field level,
# where it runs on None and crashes.
type LocalPositiveInt = Annotated[int, AfterValidator(_reject_non_positive)]


# Required fields become `T | None = None`.
class RequiredParamModel(ParamBaseModel):
    required_param: int


class AfterValidatedModel(ParamBaseModel):
    after_validated_param: LocalPositiveInt


DEFAULT_ADDED_MODELS: set[type[ParamBaseModel]] = {
    RequiredParamModel,
    AfterValidatedModel,
}

DEFAULT_ADDED_FIELD_NAMES: set[str] = {
    name for model in DEFAULT_ADDED_MODELS for name in model.model_fields
}

DEFAULT_ADDED_VALID_ARGS: Params = {
    "required_param": 0,
    "after_validated_param": 1,
}


# Non-required fields are passed through untouched
class OptionalParamModel(ParamBaseModel):
    optional_param: str = "default"


class DefaultNoneModel(ParamBaseModel):
    default_none_param: bool | None = None


UNCHANGED_MODELS: set[type[ParamBaseModel]] = {
    OptionalParamModel,
    DefaultNoneModel,
}

UNCHANGED_FIELD_NAMES: set[str] = {
    name for model in UNCHANGED_MODELS for name in model.model_fields
}

UNCHANGED_FIELD_DEFAULTS: Params = {
    "optional_param": "default",
    "default_none_param": None,
}

LIFTED_MODELS: set[type[ParamBaseModel]] = DEFAULT_ADDED_MODELS | UNCHANGED_MODELS

LIFTED_FIELD_NAMES: set[str] = DEFAULT_ADDED_FIELD_NAMES | UNCHANGED_FIELD_NAMES

TOP_LEVEL_FIELD_NAMES: set[str] = {"top_level"}

TOP_LEVEL_VALID_ARGS: Params = {"top_level": 0}

DummyModel: type[ParamBaseModel] = create_model(
    "DummyModel",
    __base__=ParamBaseModel,
    top_level=int,
    **_optional_fields(*LIFTED_MODELS),
)


def test_schema_flat_and_complete():
    """The schema is a single flat model: nested fields have been lifted to the
    top and no field is a nested Pydantic model."""
    assert set(DummyModel.model_fields) == TOP_LEVEL_FIELD_NAMES | LIFTED_FIELD_NAMES

    field: FieldInfo
    for field in DummyModel.model_fields.values():
        annotation: type[Any] | None = field.annotation
        assert not (isinstance(annotation, type) and issubclass(annotation, BaseModel))


@pytest.mark.parametrize("field_name", LIFTED_FIELD_NAMES)
def test_no_lifted_args_required(field_name: str):
    """Fields consumed only by analysis functions are never required at the top level."""
    assert not DummyModel.model_fields[field_name].is_required()


@pytest.mark.parametrize("field_name", DEFAULT_ADDED_FIELD_NAMES)
def test_default_added_implicit_none(field_name: str):
    """Omitting a field with no defaults leaves it as None."""
    assert getattr(DummyModel(**TOP_LEVEL_VALID_ARGS), field_name) is None


@pytest.mark.parametrize("field_name", DEFAULT_ADDED_FIELD_NAMES)
def test_default_added_explicit_none(field_name: str):
    """Passing an explicit None into field with no defaults is allowed.
    Explicitly-supplied values are validated, only omitted ones are skipped."""
    assert (
        getattr(DummyModel(**TOP_LEVEL_VALID_ARGS, **{field_name: None}), field_name)
        is None
    )


@pytest.mark.parametrize("field_name", DEFAULT_ADDED_FIELD_NAMES)
def test_default_added_valid_value(field_name: str):
    """A legitimate value for the field's own type is accepted and stored."""
    valid_value: Any = DEFAULT_ADDED_VALID_ARGS[field_name]

    assert (
        getattr(
            DummyModel(**TOP_LEVEL_VALID_ARGS, **{field_name: valid_value}), field_name
        )
        == valid_value
    )


@pytest.mark.parametrize("invalid_value", [0, -1])
def test_default_added_validator_preserved(invalid_value: int):
    """The rewrite deep-copies FieldInfo, so a field's own validators must still
    run: LocalPositiveInt keeps rejecting non-positive values."""
    with pytest.raises(ValidationError):
        DummyModel(**TOP_LEVEL_VALID_ARGS, after_validated_param=invalid_value)


@pytest.mark.parametrize("field_name", UNCHANGED_FIELD_NAMES)
def test_unchanged_default_preserved(field_name: str):
    """A field that already had a default keeps that default unchanged, rather
    than being forced to None."""
    assert (
        getattr(DummyModel(**TOP_LEVEL_VALID_ARGS), field_name)
        == UNCHANGED_FIELD_DEFAULTS[field_name]
    )
