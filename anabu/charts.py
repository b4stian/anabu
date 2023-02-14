#!/usr/bin/env python3

# ------------------------------------------------
# imports

try:
    import interface
    import density
    import photo
except:
    from anabu import interface
    from anabu import density
    from anabu import photo
import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, MultipleLocator
import numpy as np
import seaborn as sns

# ------------------------------------------------
# variables

# conversion factor inch to cm
CM = 0.3937007874

# width of placeholder in pptx
FIG_WIDTH = 33.5 * CM

# height of placeholder in pptx
FIG_HEIGHT = 15 * CM

# distance of ticks in scales in mm
TICK_DISTANCE = 25

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

    def __init__(self, colors: dict) -> None:
        """Read dictionary with color names and RGB tuples."""
        try:
            for item in colors.values():
                if not np.prod([value >= 0 and value <= 255 for value in item]):
                    interface.logging.exception("Expecting dictionary with RGB tuples.")
                    raise ValueError("Expecting dictionary with RGB tuples.")
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
    def convert_to_hex(rgb: tuple) -> tuple:
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

    def palette(self, color_list: list) -> sns.palettes._ColorPalette:
        """
        Return seaborn color palette with kuraray colors from color_list.
        """
        color_code_list = [self.colors[color] for color in color_list]
        return sns.color_palette(color_code_list)

    def initialize_sns_ticks(self) -> None:
        """
        Kuraray brand settings for Seaborn.
        """
        sns.set_style("ticks")
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

    def initialize_sns_grid(self) -> None:
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


def save_photo_scales(
    photo: photo.Photo, scale_factor: float, tick_distance: int = 25
) -> None:
    def create_ticks(
        photo: np.ndarray, axis: str = "x", px_mm: str = "mm", spacing: int = 10
    ) -> list:
        """
        Returns a list of axis ticks in pixels so that they are round numbers in mm.
        Spacing is the number of mm between each tick.
        """
        ticks_pixels = []
        if axis == "y":
            for i in np.arange(photo.shape[0] / 2, -1, -spacing * scale_factor):
                ticks_pixels.append(i)
            for i in np.arange(
                photo.shape[0] / 2, photo.shape[0] + 1, spacing * scale_factor
            ):
                ticks_pixels.append(i)
        elif axis == "x":
            for i in np.arange(photo.shape[1] / 2, -1, -spacing * scale_factor):
                ticks_pixels.append(i)
            for i in np.arange(
                photo.shape[1] / 2, photo.shape[1] + 1, spacing * scale_factor
            ):
                ticks_pixels.append(i)
        else:
            raise ValueError("Axis must be 'y' or 'x'.")
        ticks_pixels.pop(0)
        ticks_pixels.sort()
        ticks_mm = []
        if axis == "y":
            for i in ticks_pixels:
                ticks_mm.append(round((i - photo.shape[0] / 2) / scale_factor))
        elif axis == "x":
            for i in ticks_pixels:
                ticks_mm.append(round((i - photo.shape[1] / 2) / scale_factor))
        else:
            raise ValueError("Axis must be 'y' or 'x'.")
        if px_mm == "px":
            return ticks_pixels
        elif px_mm == "mm":
            return ticks_mm
        else:
            raise ValueError("px_mm must be 'px' or 'mm'.")

    plt.clf()
    sns.set_context("poster", font_scale=0.8)
    f, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), constrained_layout=True)
    # ax.grid(False)
    yticks = create_ticks(photo.masked_cropped_photo, "y", "px", tick_distance)
    ax.set_yticks(yticks)
    ax.set_yticklabels(
        create_ticks(photo.masked_cropped_photo, "y", "mm", tick_distance)
    )
    xticks = create_ticks(photo.masked_cropped_photo, "x", "px", tick_distance)
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        create_ticks(photo.masked_cropped_photo, "x", "mm", tick_distance)
    )
    ax.tick_params(direction="out", length=10, axis="both")
    ax.set(xlabel="x position in mm", ylabel="y position in mm")
    plt.imshow(photo.cropped_photo)
    plt.savefig(
        os.path.splitext(photo.photo_path)[0] + "_scale_axes.png",
        dpi=360,
    )
    interface.logging.info(
        f"Photo with scale axes saved to {os.path.splitext(photo.photo_path)[0] + '_scale_axes.png'}."
    )


def plot_distribution(results: density.Evaluator, path: str) -> None:
    plt.clf()
    sns.set_context("talk", font_scale=1)
    f, axes = plt.subplots(
        1, 2, figsize=(FIG_WIDTH, FIG_HEIGHT), constrained_layout=True
    )
    axes[0].plot(
        [results.brightness_peak, results.brightness_peak],
        [0, max(results.brightness_fraction) * 1.05],
        color=kuracolors_rgb["Sunrise Orange"],
    )
    axes[0].plot(
        [results.brightness_median, results.brightness_median],
        [0, max(results.brightness_fraction) * 1.05],
        color=kuracolors_rgb["Lavender"],
    )
    axes[0].plot(
        [results.brightness_mean, results.brightness_mean],
        [0, max(results.brightness_fraction) * 1.05],
        color=kuracolors_rgb["Plum"],
    )
    axes[0].axvspan(-5, 0, lw=0, facecolor=kuracolors_rgb["Sunrise Beige"], alpha=0.66)
    axes[0].axvspan(
        results.brightness_min,
        results.brightness_max,
        lw=0,
        facecolor=kuracolors_rgb["Cyan 80%"],
        alpha=0.15,
    )
    axes[0].axvspan(
        results.brightness_25,
        results.brightness_75,
        lw=0,
        facecolor=kuracolors_rgb["Cyan 80%"],
        alpha=0.35,
    )
    axes[0].axvspan(
        255, 260, lw=0, facecolor=kuracolors_rgb["Sunrise Beige"], alpha=0.65
    )
    axes[0].axhspan(
        -max(results.brightness_fraction),
        0,
        lw=0,
        facecolor=kuracolors_rgb["Sunrise Beige"],
        alpha=0.65,
    )
    sns.lineplot(
        ax=axes[0],
        x=results.brightness_array,
        y=results.brightness_fraction,
        color=kuracolors_rgb["Dark Blue 80%"],
        linewidth=3,
    )
    axes[0].set(xlabel="brightness", ylabel="fraction of pixels with brightness")
    axes[0].set_xlim(-5, 260)
    axes[0].set_ylim(-max(results.brightness_fraction) / 50)
    axes[0].xaxis.set_major_locator(MultipleLocator(25))

    axes[1].plot(
        [results.brightness_peak, results.brightness_peak],
        [0, max(results.cumulative_percentage) * 1.05],
        color=kuracolors_rgb["Sunrise Orange"],
    )
    axes[1].plot(
        [results.brightness_median, results.brightness_median],
        [0, max(results.cumulative_percentage) * 1.05],
        color=kuracolors_rgb["Lavender"],
    )
    axes[1].plot(
        [results.brightness_mean, results.brightness_mean],
        [0, max(results.cumulative_percentage) * 1.05],
        color=kuracolors_rgb["Plum"],
    )
    axes[1].axvspan(-5, 0, lw=0, facecolor=kuracolors_rgb["Sunrise Beige"], alpha=0.65)
    axes[1].axhspan(
        max(results.cumulative_percentage),
        max(results.cumulative_percentage) + 100,
        lw=0,
        facecolor=kuracolors_rgb["Sunrise Beige"],
        alpha=0.65,
    )
    axes[1].axvspan(
        results.brightness_min,
        results.brightness_max,
        lw=0,
        facecolor=kuracolors_rgb["Positive Green"],
        alpha=0.20,
    )
    axes[1].axvspan(
        results.brightness_25,
        results.brightness_75,
        lw=0,
        facecolor=kuracolors_rgb["Positive Green"],
        alpha=0.45,
    )
    axes[1].axvspan(
        255, 260, lw=0, facecolor=kuracolors_rgb["Sunrise Beige"], alpha=0.65
    )
    axes[1].axhspan(
        -max(results.cumulative_percentage),
        0,
        lw=0,
        facecolor=kuracolors_rgb["Sunrise Beige"],
        alpha=0.65,
    )
    sns.lineplot(
        ax=axes[1],
        x=results.brightness_array,
        y=results.cumulative_percentage,
        color=kuracolors_rgb["Cyan 80%"],
        linewidth=3,
    )
    axes[1].set(xlabel="brightness", ylabel="percentage of pixels (cumulative)")
    axes[1].set_xlim(-5, 260)
    axes[1].set_ylim(
        -max(results.cumulative_percentage) / 50,
        max(results.cumulative_percentage) + 15,
    )
    axes[1].yaxis.set_major_locator(FixedLocator([i * 10 for i in range(10 + 1)]))
    axes[1].xaxis.set_major_locator(MultipleLocator(25))

    plt.savefig(
        path,
        dpi=360,
    )
    interface.logging.info(f"Distribution plot saved to {path}.")


def run_charts() -> None:
    color_scheme.initialize_sns_ticks()
    save_photo_scales(photo.photo, photo.SCALE_FACTOR, TICK_DISTANCE)
    color_scheme.initialize_sns_grid()
    plot_distribution(
        density.evaluator,
        os.path.splitext(photo.photo.photo_path)[0] + "_distribution_plot.png",
    )

# ------------------------------------------------
# executions

color_scheme = Kurascheme(kuracolors_rgb)
color_scheme.to_hex()
kurapalette = color_scheme.palette(palette_list)
interface.logging.info("Defined Kuraray color palette")

is_main = __name__ == "__main__"

if is_main:
    interface.run_interface()
    photo.run_photo()
    density.run_density()
    color_scheme.initialize_sns_ticks()
    save_photo_scales(photo.photo, photo.SCALE_FACTOR, TICK_DISTANCE)
    color_scheme.initialize_sns_grid()
    plot_distribution(
        density.evaluator,
        os.path.splitext(photo.photo.photo_path)[0] + "_distribution_plot.png",
    )
