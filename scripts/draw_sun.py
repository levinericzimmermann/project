import os
import math
import subprocess

import cairo
import jinja2


def draw_sun(filename, movement):
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

    cr.set_line_width(0.02)

    color = (0, 0, 0, 1)

    xc = 0.5
    yc = 0.4
    radius = 0.25

    xh, yh = 0.5, 0.85

    _draw_horizon(cr, color)

    match movement:
        # sunrise
        case 0:
            _draw_half_sun(cr, color, xh, yh, radius)
            _draw_arrow_rise(cr, color)
        # daylight
        case 1:
            _draw_full_sun(cr, color, xc, yc, radius)
        # sunset
        case 2:
            _draw_half_sun(cr, color, xh, yh, radius)
            _draw_arrow_fall(cr, color)
        # night
        case 3:
            pass
        case _:
            raise NotImplementedError()

    surface.write_to_png(filename)


def _draw_horizon(cr, color):
    cr.set_source_rgba(*color)
    cr.move_to(0, 0.85)
    cr.line_to(1, 0.85)
    cr.stroke()


def _draw_full_sun(cr, color, xc, yc, radius):
    angle1 = 0 * (math.pi / 180.0)  # angles are specified
    angle2 = 360 * (math.pi / 180.0)  # in radians
    _draw_sun(cr, color, xc, yc, radius, angle1, angle2)


def _draw_half_sun(cr, color, xc, yc, radius):
    angle1 = 180 * (math.pi / 180.0)  # angles are specified
    angle2 = 360 * (math.pi / 180.0)  # in radians
    _draw_sun(cr, color, xc, yc, radius, angle1, angle2)


def _draw_sun(cr, color, xc, yc, radius, angle1, angle2):
    cr.set_source_rgba(*color)
    cr.arc(xc, yc, radius, angle1, angle2)
    cr.stroke()


def _draw_arrow_rise(cr, color):
    cr.set_line_width(0.007)

    cr.move_to(0.5, 0.55)
    cr.line_to(0.5, 0.4)
    cr.stroke()

    cr.move_to(0.502, 0.4)
    cr.line_to(0.475, 0.425)
    cr.stroke()

    cr.move_to(0.498, 0.4)
    cr.line_to(0.525, 0.425)
    cr.stroke()


def _draw_arrow_fall(cr, color):
    cr.set_line_width(0.007)

    cr.move_to(0.5, 0.55)
    cr.line_to(0.5, 0.4)
    cr.stroke()

    cr.move_to(0.502, 0.55)
    cr.line_to(0.475, 0.525)
    cr.stroke()

    cr.move_to(0.498, 0.55)
    cr.line_to(0.525, 0.525)
    cr.stroke()


def _draw_arrow_round(cr, color):
    angle0, angle1 = (x * (math.pi / 180) for x in (180, 270))
    cr.set_line_width(0.005)
    cr.set_source_rgba(*color)
    cr.arc(0.6, 0.5, 0.1, angle0, angle1)
    cr.stroke()

    cr.move_to(0.599, 0.401)
    cr.line_to(0.575, 0.385)
    cr.stroke()

    cr.move_to(0.599, 0.399)
    cr.line_to(0.575, 0.425)
    cr.stroke()


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=etc/suncycle/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))


if __name__ == "__main__":
    for movement in range(4):
        path = f"etc/suncycle/sun_{movement}"
        img_path = f"{path}.png"
        draw_sun(img_path, movement)
        for landscape in (True, False):
            tex_path = path
            if landscape:
                tex_path = f"{path}_landscape"
            tex_path = f"{tex_path}.tex"
            template = J2ENVIRONMENT.get_template("sun.tex.j2").render(
                path=img_path, landscape=landscape
            )
            with open(tex_path, "w") as b:
                b.write(template)
            call_latex(tex_path)
