from mutwo.project_parameters import Poem as p
from mutwo.project_parameters import Translator as t

from . import week

POEM_TUPLE = (
    p(
        "91",
        r"""In memory

Of Pelagon, a fisherman,
his father Meniscus placed

here a fishbasket and oar:
tokens of an unlucky life""",
    ),
    p(
        "61",
        r"""Pain penetrates

Me drop
by drop""",
    ),
    p(
        "56",
        r"""Day in, day out

I hunger and
I struggle""",
    ),
    p(
        "26",
        r"""The evening star

Is the most
beautiful
of all stars""",
    ),
    p(
        "168B",
        r"""The Moon and Pleiades have set –
half the night is gone.
Time passes.
I sleep alone.""",
        t.RAYOR,
    ),
    p(
        "154",
        r"""As the full moon rose,
women stood round the altar.""",
        t.RAYOR,
    ),
    p(
        "91",
        r"""In memory

Of Pelagon, a fisherman,
his father Meniscus placed

here a fishbasket and oar:
tokens of an unlucky life.""",
    ),
)


POEM_DICT = {p.name: p for p in POEM_TUPLE}

# Order of poems, each day has it's own poem.
POEM_NAME_TUPLE = ("168B", "91", "56", "154", "26", "61", "168B")

WEEK_DAY_TO_POEM = {
    week_day: POEM_DICT[poem_name]
    for week_day, poem_name in zip(week.WeekDay, POEM_NAME_TUPLE)
}


del t, p, week
