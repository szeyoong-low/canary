from copy import deepcopy
from typing import Optional

from pydantic import create_model
from pydantic.fields import FieldInfo

from ..display.charts import DisplayFunctionName
from ..global_types import Params
from .models import EntityParam
from ..transformations.models import DateIndex, TimeHorizon, WindowFunction
from ..validators.primitives import DateRangeModel, ParamBaseModel


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
            if field_info.is_required():
                # The declared type of the attribute is type[Any] | None.
                # Optional is evaluated at runtime, so it operates on the
                # actual value, not on the declared type.
                field_copy: FieldInfo = deepcopy(field_info)
                field_copy.default = None
                # Default values are not validated, so field validators can stay
                fields[field_name] = (Optional[field_copy.annotation], field_copy)
            else:
                fields[field_name] = (field_info.annotation, field_info)

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

    return {
        name: (field.annotation, field)
        for model in models
        for name, field in model.model_fields.items()
    }


"""
Pydantic models that form schemas for terminal functions used as agent tools.
Validators are omitted as top-level models only contain types and documentation.
Actual (strict) validation is done by analysis functions on the specific
arguments they consume.
"""

# To support legacy REST endpoint
AssetPriceDailyAPI = create_model(
    "AssetPriceDailyAPI",
    __base__=ParamBaseModel,
    # Args required for seeding
    **_required_fields(DateRangeModel),
    # Args consumed by analysis functions (with required ones made optional)
    **_optional_fields(DateIndex, TimeHorizon, WindowFunction),
)

AssetPriceDailySchema = create_model(
    "AssetPriceDailySchema",
    __base__=ParamBaseModel,
    # Args required for orchestration
    display=DisplayFunctionName,
    analysis=set[str],
    symbol=EntityParam,
    # Args required for seeding
    **_required_fields(DateRangeModel),
    # Args consumed by analysis functions (with required ones made optional)
    **_optional_fields(DateIndex, TimeHorizon, WindowFunction),
)
