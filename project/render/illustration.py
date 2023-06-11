import os
import subprocess

import abjad
import jinja2
import ranges

from mutwo import abjad_converters

import project


def illustration():
    base_path = "builds/illustrations"
    intro_tex_path = f"{base_path}/intro.tex"
    poem_tex_path = f"{base_path}/poem.tex"

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    illustrate_start(intro_tex_path)
    illustrate_poem(poem_tex_path)


def illustrate_start(tex_path):
    template = J2ENVIRONMENT.get_template("intro.tex.j2").render()
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def illustrate_poem(tex_path):
    template = J2ENVIRONMENT.get_template("poem.tex.j2").render(
        poem_list=[p for p in project.constants.WEEK_DAY_TO_POEM.values()]
    )
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/illustrations/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))
