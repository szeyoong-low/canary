from coloraide import Color

from ..global_constants import TRANSFORMATION_SEPARATOR
from ..global_types import Column, Entities
from .models import ChartConfigModel, ItemStyle, LineStyle, Series

"""Add legend and series to chart config"""

type ColorKey = str
type ColorSlot = int
type ColorMapping = dict[str, ColorSlot]
type HexColor = str

# Visually equidistant palette
# https://www.learnui.design/tools/data-color-picker.html#palette
BASE_HUES: list[str] = [
    "#003d5c",
    "#31497e",
    "#674f95",
    "#a14e9a",
    "#d44c8d",
    "#f9596f",
    "#ff7a47",
    "#ffa600",
    "#acacac",  # Others
]
MAX_HUE_SLOT: int = len(BASE_HUES) - 1
LIGHTNESS_CEILING: float = 0.85
TINT_STEP: float = 0.09
MAX_TINTS: int = 5


def _tint(base_hex: HexColor, step: int) -> HexColor:
    """Lighten a base hue by `step` OKLCH lightness increments."""

    base: Color = Color(base_hex).convert("oklch")

    lightness: float = min(base["lightness"] + step * TINT_STEP, LIGHTNESS_CEILING)
    tinted: Color = Color("oklch", [lightness, base["chroma"], base["hue"]])
    return tinted.convert("srgb").to_string(hex=True)


def _style_lines(
    chart_config: ChartConfigModel, lines: list[Column], entities: Entities, key: Column
) -> ChartConfigModel:

    # Order of appearance decides the slot (the columns are already ordered
    # individual first by entity name, then collective).
    hue_mapping: ColorMapping = {}
    tint_mapping: ColorMapping = {}

    for line in lines:
        # `<entity>/<value>` for individual metrics, `<value>` for collective
        entity: str
        analysis: str
        entity, _, analysis = line.partition(TRANSFORMATION_SEPARATOR)

        hue_key: ColorKey
        tint_key: ColorKey | None
        if entity in entities:
            # Individual: hue = entity, tint = transformation
            hue_key, tint_key = entity, analysis
        else:
            # Collective: one hue
            hue_key, tint_key = line, None

        hue_slot: ColorSlot = hue_mapping.setdefault(
            # Push into "Others" if there are more than MAX_HUE_SLOT to distinguish
            hue_key,
            min(len(hue_mapping), MAX_HUE_SLOT),
        )

        tint_slot: ColorSlot
        if tint_key is None:
            tint_slot = 0
        else:
            tint_slot = tint_mapping.setdefault(tint_key, len(tint_mapping))
            if tint_slot >= MAX_TINTS:
                raise ValueError(
                    f"Can distinguish between a maximum of {MAX_TINTS} individual metrics"
                )

        color: HexColor = _tint(BASE_HUES[hue_slot], tint_slot)
        chart_config.series.append(
            Series(
                name=line,
                type="line",
                encode={"x": key, "y": line},
                lineStyle=LineStyle(color=color),
                itemStyle=ItemStyle(color=color),
                showSymbol=False,
            )
        )

    chart_config.legend.data = list(lines)
    chart_config.tooltip.trigger = "axis"

    return chart_config
