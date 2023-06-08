import os
import subprocess

import abjad
import jinja2
import ranges

from mutwo import abjad_converters


def illustration():
    base_path = "builds/illustrations"
    intro_tex_path = f"{base_path}/intro.tex"

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    illustrate_start(
        intro_tex_path,
    )


def illustrate_start(tex_path):
    template = J2ENVIRONMENT.get_template("intro.tex.j2").render()
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/illustrations/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))
