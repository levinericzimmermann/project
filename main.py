from mutwo import kepathian_converters
from mutwo import project_converters

import project

# for i, s in enumerate(project.constants.SENTENCE_TUPLE):
#     print(i, s)
#     print('')
# 1/0

# seq = project.mmml.parse('project/mmml/0.mmml')


content_to_document = kepathian_converters.ContentToDocument()
page_index_to_spread = project_converters.PageIndexToSpread()
content_list = [
    r"""\nofolios
\begin{center}
\font[size=24pt]{11.1}
\end{center}
"""
]
for page_index in range(project.constants.PAGE_COUNT):
    content_list.append(page_index_to_spread.convert(page_index))

content = "\n\n\\pagebreak\n\n".join(content_list)
content_to_document.convert(content, r"builds/11.1.pdf", cleanup=False)
