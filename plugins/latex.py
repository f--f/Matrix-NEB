from neb.plugins import Plugin
import sympy
import pyglet

from io import BytesIO

# todo:
# incorporate state? like changing default font size (modify preamble), dvioptions
# catch runtime error in _render

class LatexPlugin(Plugin):
    """Render LaTeX to images.
    !latex eq <source> : Return equation <source> as image.
    """

    name="latex"

    def cmd_run(self, event, *args):
        src = event["content"]["body"][10:].strip()
        try:
            image = self._render(src)
            pyg = pyglet.image.load(".png", file=image) # for image metadata
            media = self.matrix.media_upload(image.getvalue(), "image/png")
            self.matrix.send_content(
                event["room_id"],
                media["content_uri"],
                src[:30],  # limit filename to 30 characters to avoid taking up too much space
                "m.image",
                # can leave out metadata but might mess up thumbnails? not sure
                {"h": pyg.height, "w": pyg.width, "mimetype": "image/png", "size": len(image.getvalue())} 
            )
        except RuntimeError as e:
            return str(e)


    def _render(self, src):
        """Render an image of the compiled LaTeX source to memory."""
        image = BytesIO()
        sympy.preview(
            # sympy.preview expects a str expression, but src is unicode object
            # so need to pass to sympy.latex first
            sympy.latex(src, mode="plain"),
            output="png",
            viewer="BytesIO",
            outputbuffer=image,
            # options for dvipng utility
            dvioptions=["-T", "tight", "-z", "9", "--truecolor"],
            # latex preamble
            preamble=r"\documentclass[12pt]{article}\pagestyle{empty}\usepackage{amsmath}\begin{document}"
        )
        return image