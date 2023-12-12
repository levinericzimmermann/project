from mutwo import abjad_converters
from mutwo import project_parameters

abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = (
    abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    + (project_parameters.BreathIndicator(),)
)
