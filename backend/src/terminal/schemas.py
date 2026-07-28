from copy import deepcopy
from inspect import cleandoc

from pydantic import create_model
from pydantic.fields import FieldInfo

from ..display.charts import DisplayFunctionName
from ..global_types import Column, ColumnOptional, Params
from ..transformations.models import DateIndex, TimeHorizon, WindowFunction
from ..validators.primitives import DateRangeModel, ParamBaseModel
from .models import EntityParam, MarketDrilldownParam


def _contextualise_field(
    field_info: FieldInfo, model: type[ParamBaseModel]
) -> FieldInfo:
    """Copy the field and append the docstring of its containing model."""
    field_copy: FieldInfo = deepcopy(field_info)  # Models are shared by tools
    field_copy.description = (
        " ".join(filter(None, (field_copy.description, cleandoc(model.__doc__ or ""))))
        or None
    )
    return field_copy


def _optional_fields(*models: type[ParamBaseModel]) -> Params:
    """
    Merge several leaf models' fields into one dict with every required field
    (no default) made optional (... | None = None)

    Args:
        A packed list of Pydantic models. Their fields' validators and
        description live in FieldInfo's .metadata/.description, not .annotation.

    Returns: Dictionary of keyword arguments to be passed into `create_model`
        containing values tuple[Any, FieldInfo], the first being a type and the
        second being the assigned value (a default or a FieldInfo).

        The value is documented as Any because Pylance cannot rule out key
        collisions with keyword-only arguments that cause assignments to them
        of the wrong type. Anyways, `dict[Any, Any]` is the documented type of
        the packed keyword arguments accepted by `create_model`.
    """

    fields: Params = {}

    for model in models:
        for field_name, field_info in model.model_fields.items():
            field_copy: FieldInfo = _contextualise_field(field_info, model)

            if field_copy.is_required():
                # The declared type of the attribute is type[Any] | None.
                # Optional is evaluated at runtime, so it operates on the
                # actual value, not on the declared type.
                field_copy.default = None

                if field_copy.annotation is None:
                    # Necessary as None has no __or__ method for union construction
                    fields[field_name] = (None, field_copy)
                else:
                    # Default values are not validated, so field validators can stay
                    fields[field_name] = (field_copy.annotation | None, field_copy)
            else:
                fields[field_name] = (field_copy.annotation, field_copy)

    return fields


def _required_fields(*models: type[ParamBaseModel]) -> Params:
    """
    Merge several leaf models' fields into one dict with fields left as-is

    Args:
        A packed list of Pydantic models. Their fields' validators and
        description live in FieldInfo's .metadata/.description, not .annotation.

    Returns: Dictionary of keyword arguments to be passed into `create_model`
        containing values tuple[Any, FieldInfo], the first being a type and the
        second being the assigned value (a default or a FieldInfo).

        The value is documented as Any because Pylance cannot rule out key
        collisions with keyword-only arguments that cause assignments to them
        of the wrong type. Anyways, `dict[Any, Any]` is the documented type of
        the packed keyword arguments accepted by `create_model`.
    """

    fields: Params = {}

    for model in models:
        name: str
        field_info: FieldInfo
        for name, field_info in model.model_fields.items():
            field_copy: FieldInfo = _contextualise_field(field_info, model)
            fields[name] = (field_copy.annotation, field_copy)

    return fields


"""
Pydantic models that form schemas for terminal functions used as agent tools.
Validators are omitted as top-level models only contain types and documentation.
Actual (strict) validation is done by analysis functions on the specific
arguments they consume.
"""


class AssetPriceDailyParams(ParamBaseModel):
    display: DisplayFunctionName
    analysis: set[str]
    symbol: EntityParam


# To support legacy REST endpoint
AssetPriceDailyAPI: type[ParamBaseModel] = create_model(
    "AssetPriceDailyAPI",
    __base__=ParamBaseModel,
    # Args required for seeding
    **_required_fields(DateRangeModel),
    # Args consumed by analysis functions (with required ones made optional)
    **_optional_fields(DateIndex, TimeHorizon, WindowFunction),
)

AssetPriceDailySchema: type[ParamBaseModel] = create_model(
    "AssetPriceDailySchema",
    __base__=ParamBaseModel,
    # Args required for orchestration and seeding
    **_required_fields(AssetPriceDailyParams, DateRangeModel),
    # Args consumed by analysis functions (with required ones made optional)
    **_optional_fields(DateIndex, TimeHorizon, WindowFunction),
)


class MarketCompositionParams(ParamBaseModel):
    display: DisplayFunctionName
    analysis: set[str]
    drilldown: MarketDrilldownParam
    aggregate_col: Column
    colour_col: ColumnOptional = None


# To support legacy REST endpoint
MarketCompositionAPI: type[ParamBaseModel] = create_model(
    "MarketCompositionAPI",
    __base__=ParamBaseModel,
)

MarketCompositionSchema: type[ParamBaseModel] = create_model(
    "MarketCompositionSchema",
    __base__=ParamBaseModel,
    # Args required for orchestration and seeding
    **_required_fields(MarketCompositionParams),
)
