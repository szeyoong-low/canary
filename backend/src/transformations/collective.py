from .constants import TransformationDispatch

"""Compute values for all entities"""


# Invariant: Transformations must be registered in exactly one of
# INDIVIDUAL_TRANSFORMATIONS or COLLECTIVE_TRANSFORMATIONS
COLLECTIVE_TRANSFORMATIONS: TransformationDispatch = {}
