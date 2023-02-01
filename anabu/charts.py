#!/usr/bin/env python3

# ------------------------------------------------
# imports

try:
    import interface
    import density
except:
    from anabu import interface
    from  anabu import density
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------
# variables

# conversion factor inch to cm
CM = 0.3937007874

# width of placeholder in pptx
FIG_WIDTH = 33.5 * CM 

# height of placeholder in pptx
FIG_HEIGHT = 15 * CM

# Kuraray color scheme from branding homepage
kuracolors_rgb = {
    "Cyan 80%": (0, 176, 233),
    "Dark Blue": (0, 15, 60),
    "White": (255, 255, 255),
    "Cyan 50%": (96, 206, 241),
    "Cyan 40%": (128, 215, 244),
    "Cyan 30%": (159, 225, 247),
    "Cyan 20%": (191, 235, 249),
    "Cyan 10%": (223, 245, 252),
    "Cyan 5%": (239, 250, 254),
    "Dark Blue 80%": (51, 63, 99),
    "Dark Blue 70%": (77, 87, 119),
    "Dark Blue 60%": (102, 111, 138),
    "Dark Blue 50%": (128, 135, 157),
    "Dark Blue 40%": (153, 159, 177),
    "Dark Blue 30%": (178, 183, 196),
    "Dark Blue 20%": (204, 207, 216),
    "Dark Blue 10%": (229, 231, 235),
    "Dark Blue 5%": (242, 243, 245),
    "Sunrise Beige": (214, 210, 196),
    "Sunrise Yellow": (255, 200, 69),
    "Sunrise Orange": (255, 134, 114),
    "Sunrise Purple": (161, 146, 178),
    "Sunrise Beige 80%": (222, 219, 208),
    "Sunrise Beige 60%": (230, 228, 220),
    "Sunrise Beige 40%": (239, 237, 231),
    "Sunrise Beige 20%": (247, 246, 243),
    "Sunrise Yellow 80%": (255, 211, 106),
    "Sunrise Yellow 60%": (255, 222, 143),
    "Sunrise Yellow 40%": (255, 233, 181),
    "Sunrise Yellow 20%": (255, 244, 218),
    "Sunrise Orange 80%": (255, 162, 150),
    "Sunrise Orange 60%": (255, 185, 176),
    "Sunrise Orange 40%": (255, 209, 203),
    "Sunrise Orange 20%": (255, 232, 229),
    "Sunrise Purple 80%": (180, 168, 193),
    "Sunrise Purple 60%": (199, 190, 209),
    "Sunrise Purple 40%": (217, 211, 224),
    "Sunrise Purple 20%": (236, 233, 240),
    "Positive Green": (117, 185, 108),
    "Tangerine": (255, 167, 90),
    "Coral": (236, 103, 105),
    "Warning Red": (217, 71, 95),
    "Plum": (189, 108, 136),
    "Lavender": (80, 79, 118),
}

palette_list = [
    "Cyan 80%",
    "Sunrise Orange",
    "Positive Green",
    "Lavender",
    "Plum",
    "Dark Blue 60%",
    "Sunrise Yellow",
    "Warning Red",
    "Sunrise Purple",
    "Tangerine",
    "Dark Blue 40%",
    "Coral",
    "Cyan 40%",
    "Sunrise Beige",
    "Sunrise Purple 60%",
    "Sunrise Orange 60%",
    "Sunrise Yellow 60%",
    "Dark Blue 20%",
    "Cyan 20%",
]

# ------------------------------------------------
# function/class definitions


class Kurascheme:
    """Kuraray color scheme."""

    def __init__(self, colors:dict) -> None:
        """Read dictionary with color names and RGB tuples."""        
        try:
            for item in colors.values():
                if not np.prod([value >= 0 and value <= 255 for value in item]):
                    interface.logging.exception(
                        "Expecting dictionary with RGB tuples."
                    )
                    raise ValueError(
                        "Expecting dictionary with RGB tuples."
                    )
        except:
            interface.logging.exception(
                f"Expecting dictionary with RGB tuples. Check your color scheme. {colors}"
            )
            raise ValueError(
                f"Expecting dictionary with RGB tuples. Check your color scheme. {colors}"
            )
        self.colors = colors

    def __repr__(self) -> str:
        return f"Kuraray color scheme: {str(self.colors)}"

    @staticmethod
    def convert_to_hex(rgb:tuple) -> tuple:
        """
        Convert a color from rgb to hexadecimal.
        """
        return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

    def to_hex(self) -> None:
        """
        Convert color scheme from RGB to hex.
        """
        for item in self.colors:
            self.colors[item] = self.convert_to_hex(self.colors[item])
            
    def palette(self, color_list:list) -> sns.palettes._ColorPalette:
        """
        Return seaborn color palette with kuraray colors from color_list.
        """
        color_code_list = [self.colors[color] for color in color_list]
        return sns.color_palette(color_code_list)

    def initialize_sns(self) -> None:
        """
        Kuraray brand settings for Seaborn.
        """
        sns.set_style("whitegrid")
        sns.set_theme(
            font="Rational Display",
            style={
                "axes.facecolor": self.colors["Sunrise Beige 20%"],
                "text.color": self.colors["Dark Blue"],
                "axes.labelcolor": self.colors["Dark Blue"],
                "xtick.color": self.colors["Dark Blue"],
                "ytick.color": self.colors["Dark Blue"],
            },
        )
        interface.logging.info("Set Kuraray brand settings for plots.")
        
# TODO Draw scalebars around cropped photo.

# TODO distributions

# ------------------------------------------------
# executions

    color_scheme = Kurascheme(kuracolors_rgb)
    color_scheme.to_hex()
    kurapalette = color_scheme.palette(palette_list)
    interface.logging.info("Defined Kuraray color palette")
    color_scheme.initialize_sns()

is_main = __name__ == "__main__"

if is_main:
    pass