import inspect

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import project_parameters

abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = tuple(
    a
    for a in abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    if a.__name__ not in ("Tremolo",)
) + tuple(
    cls
    for _, cls in inspect.getmembers(project_parameters, inspect.isclass)
    if not inspect.isabstract(cls)
    and abjad_parameters.abc.AbjadAttachment in inspect.getmro(cls)
)


del inspect, abjad_converters, abjad_parameters, project_parameters
