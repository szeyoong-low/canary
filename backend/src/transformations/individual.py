from .constants import TransformationDispatch

"""Compute values for a single entity"""


# Invariant: Transformations must be registered in exactly one of
# INDIVIDUAL_TRANSFORMATIONS or COLLECTIVE_TRANSFORMATIONS
INDIVIDUAL_TRANSFORMATIONS: TransformationDispatch = {}
