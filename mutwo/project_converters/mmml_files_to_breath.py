from mutwo import breath_converters
from mutwo import core_converters
from mutwo import core_utilities
from mutwo import kepathian_converters
from mutwo import kepathian_events

import project


class PageIndexToBreathSequenceTuple(core_converters.abc.Converter):
    def __init__(self):
        self._logger = core_utilities.get_cls_logger(type(self))

    def convert(self, page_index: int) -> tuple[kepathian_events.KTable, ...]:
        path = f"project/mmml/{page_index}.mmml"
        try:
            return project.mmml.parse(path)
        except FileNotFoundError:
            self._logger.warn(f"no music for page {page_index + 1}")
            return self.convert(0)


class PageIndexToKTableTuple(core_converters.abc.Converter):
    def __init__(
        self,
        breath_sequence_to_ktable=breath_converters.BreathSequenceToKTable(),
        page_index_to_breath_sequence_tuple=PageIndexToBreathSequenceTuple(),
    ):
        self.breath_sequence_to_ktable = breath_sequence_to_ktable
        self.page_index_to_breath_sequence_tuple = page_index_to_breath_sequence_tuple

    def convert(self, page_index: int) -> tuple[kepathian_events.KTable, ...]:
        breath_sequence_tuple = self.page_index_to_breath_sequence_tuple.convert(
            page_index
        )
        ktable_list = []
        for breath_sequence in breath_sequence_tuple:
            ktable = self.breath_sequence_to_ktable.convert(breath_sequence)
            ktable_list.append(ktable)
        return tuple(ktable_list)


class PageIndexToMusic(core_converters.abc.Converter):
    def __init__(
        self,
        page_index_to_ktable_tuple: PageIndexToKTableTuple = PageIndexToKTableTuple(),
        ktable_to_sile_str: kepathian_converters.KTableToSileStr = kepathian_converters.KTableToSileStr(),
        content_to_document: kepathian_converters.ContentToDocument = kepathian_converters.ContentToDocument(),
    ):
        self.i2ktable_tuple = page_index_to_ktable_tuple
        self.ktable_to_sile_str = ktable_to_sile_str
        self.content_to_document = content_to_document

    def convert(self, page_index: int) -> str:
        ktable_tuple = self.i2ktable_tuple.convert(page_index)
        content = "\n\n".join(
            [self.ktable_to_sile_str.convert(ktable) for ktable in ktable_tuple]
        )
        result = (
            f" \\glue[width=20cm]-\\skip[height=4cm]\n\n\\glue[width=2cm]{content}\n\n"
        )
        return (
            r"\font[filename=etc/fonts/jetb/ttf/JetBrainsMonoNL-Regular.ttf]"
            f"\n{result}"
        )


class PageIndexToText(core_converters.abc.Converter):
    abc = "abcdefghijklmnopqrstuvwxyz" + "äöüß"

    def convert(self, page_index: int) -> str:
        sentence = project.constants.SENTENCE_TUPLE[page_index]
        word_tuple = sentence.split(" ")
        word_list = []
        for word in word_tuple:
            split_word = []
            for c in word:
                if c in self.abc:
                    split_word.append(c)
                else:
                    word_list.append("".join(split_word))
                    split_word = []
                    word_list.append(c)
            if split_word:
                word_list.append("".join(split_word))
        # return "\n\n".join(word_list)
        result = _table(word_list)
        ragged = "raggedright" if page_index % 2 == 0 else "raggedleft"
        # return rf"""\font[filename=etc/fonts/Space_Mono/SpaceMono-Regular.ttf]
        return rf"""\font[filename=etc/fonts/schwabacher/alte-schwabacher/AlteSchwabacher.ttf,size=6pt]
\begin{{{ragged}}}
{result}
\end{{{ragged}}}
"""


def _table(word_list):
    t = r"\kepathian{" "\n"
    for word in word_list:
        row = r"\tr{" "\n"
        for c in word:
            row += r"\td{" + c + r"\glue[width=0.65cm]" + "}\n"
        row += "}\n"
        t += row
    t += "}"
    return t


class PageIndexToSpread(core_converters.abc.Converter):
    def __init__(
        self,
        page_index_to_text: PageIndexToText = PageIndexToText(),
        page_index_to_music: PageIndexToMusic = PageIndexToMusic(),
    ):
        self.i2text = page_index_to_text
        self.i2music = page_index_to_music

    def convert(self, page_index: int) -> str:
        data = [
            self.i2text(page_index),
            self.i2music(page_index),
        ]
        if page_index % 2 == 1:
            data.reverse()
        return "\n\n\\pagebreak\n\n".join(data)
