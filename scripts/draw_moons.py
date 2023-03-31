import os
from math import pi
import subprocess

import cairo
import jinja2

from mutwo import core_events

envelope = core_events.Envelope([[0, 0, 3], [0.5, 1], [1, 1]])


def draw_moon(filename, movement):
    reverse = True
    if movement < 0:
        movement = abs(movement)
        reverse = False

    width, height = 2000, 2000
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)

    cr.scale(width, height)

    cr.save()

    pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
    pat.add_color_stop_rgba(1, 1, 1, 1, 1)

    cr.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
    cr.set_source(pat)
    cr.fill()

    cr.set_line_width(0.04)

    color0 = (0, 0, 0, 1)
    color1 = (1, 1, 1, 1)

    xc = 0.5
    yc = 0.5
    radius = 0.35

    if movement == 1:
        _drawa0full(cr, color0, movement, xc, yc, radius)
    elif movement:
        _drawa0(cr, color0, movement, xc, yc, radius)
        _drawa1(cr, movement, radius, color1)
        _drawa2(cr, movement, color0)

    surface.write_to_png(filename)

    if reverse:
        t_filename = ".rotated.png"
        subprocess.call(["convert", filename, "-distort", "SRT", "-180", t_filename])
        os.remove(filename)
        subprocess.call(["mv", t_filename, filename])


def _drawa0(cr, color0, movement, xc, yc, radius):
    angle_factor = envelope.value_at(abs(movement))
    # angle_factor = 0

    angle_value = 90 * angle_factor
    angle1 = angle_value * (pi / 180.0)  # angles are specified
    angle2 = (360 - angle_value) * (pi / 180.0)  # in radians

    cr.set_source_rgba(*color0)
    cr.arc(xc, yc, radius, angle1, angle2)
    cr.fill()


def _drawa0full(cr, color0, movement, xc, yc, radius):
    cr.set_source_rgba(*color0)
    cr.arc(xc, yc, radius, 0, 360 * (pi / 180))
    cr.fill()


def _drawa1(cr, movement, radius, color1):
    cr.save()

    x = 0
    y = 0
    cr.translate(x + 1 / 2.0, y + 1 / 2.0)
    n = core_events.Envelope([[0, -0.2, 3], [0.5, -1.99999999], [1, 0]]).value_at(
        movement
    )
    cr.scale(2 / 2, 2 / (2 + n))

    tolerance = 0.0001
    if movement > 0.5:
        xc2_factor_movement = 0.5
    else:
        xc2_factor_movement = movement
    xc2_factor = ((radius * 2) + tolerance) * xc2_factor_movement
    xc2 = xc2_factor

    cr.set_source_rgba(*color1)
    cr.arc(xc2, 0, radius + tolerance, 0, 360 * (pi / 180.0))
    cr.fill()
    cr.restore()


def _drawa2(cr, movement, color0):
    if movement > 0.5:
        cr.save()
        cr.set_source_rgba(*color0)
        x = 0
        y = 0
        cr.translate(x + 1 / 2.0, y + 1 / 2.0)
        n = core_events.Envelope([[0, 100], [0.5, 15, -4], [1, 0]]).value_at(movement)
        cr.scale(2 / (2 + n), 2 / 2)
        cr.arc(-0.008, 0, 0.35, 270 * (pi / 180), 450 * (pi / 180.0))
        cr.fill()
        cr.restore()


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=etc/mooncycle/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))


if __name__ == "__main__":
    penvelope = core_events.Envelope([[0, 0], [15, 1], [16, -1], [30, 0]])
    m = 15
    for i in range(30):
        path = f"etc/mooncycle/m{i}"
        img_path = f"{path}.png"
        pdf_path = f"{path}.pdf"
        p = penvelope.value_at(i)
        draw_moon(img_path, p)
        for landscape in (True, False):
            tex_path = path
            if landscape:
                tex_path = f"{path}_landscape"
            tex_path = f"{tex_path}.tex"
            template = J2ENVIRONMENT.get_template("moon.tex.j2").render(
                path=img_path, landscape=landscape
            )
            with open(tex_path, "w") as b:
                b.write(template)
            call_latex(tex_path)
