import typing

from mutwo import kepathian_converters
from mutwo import project_converters

import project


def notation(page_count: typing.Optional[int] = None):
    content_to_document = kepathian_converters.ContentToDocument()
    page_index_to_spread = project_converters.PageIndexToSpread()
    content_list = []

    with open("etc/templates/cover.sil") as f:
        content_list.append(f.read())

    for page_index in range(page_count or project.constants.PAGE_COUNT):
        content_list.append(page_index_to_spread.convert(page_index))

    content = "\n\n\\pagebreak\n\n".join(content_list)
    content_to_document.convert(content, r"builds/11.1.pdf", cleanup=False)
