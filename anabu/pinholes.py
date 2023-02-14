#!/usr/bin/env python3

"""
Pinhole evaluator
"""

# ------------------------------------------------
# imports

try:
    import interface
    import photo
except:
    from anabu import interface
    from anabu import photo

import csv
import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import skimage as sm

# ------------------------------------------------
# variables

# calibration parameters from microscopic pinhole measurements
# FIXME correct! Is this 175?
CALIBRATION_1 = {
    "name": "Calibration 1",
    "date": "2022-07-09",
    "threshold": 175,
    "parameters": [
        2.97879300e00,
        -1.16214041e-02,
        2.67696227e-05,
        1.79613183e-09,
    ],
    "minimum_size": 6,
    "exposure_time": 30.0,
}

# Diameters for pinhole size categories
PINHOLE_CLASS_STEPS = [50, 100, 150, 350]

# ------------------------------------------------
# function/class definitions


class Pinholer:
    """
    Find pinholes in photo.
    """

    def __init__(self, photo: photo.Photo) -> None:
        attributes_inherit = {
            "sample_name",
            "cropped_photo",
            "cropped_mask",
            "photo_path",
            "save_image",
        }
        if not "cropped_photo" in photo.__dict__.keys():
            photo.cropped_photo = photo.photo
        if not "cropped_mask" in photo.__dict__.keys():
            photo.cropped_mask = photo.mask
        for attr in attributes_inherit:
            try:
                setattr(self, attr, getattr(photo, attr))
            except:
                interface.logging.exception(
                    f"Attribute {attr} missing in {photo}. Cannot initiate Pinholer object."
                )
                raise Exception(
                    f"Attribute {attr} missing in {photo}. Cannot initiate Pinholer object."
                )
        interface.logging.info(f"Initiated Pinholer object for {self.sample_name}.")
        # TODO select best calibration based on photo details or via input.
        self.calibration_pinholes = CALIBRATION_1
        self.minimum_size_calibration_pinholes = self.conv_pixel_diameter(
            self.calibration_pinholes["minimum_size"]
        )
        interface.results.add_result(
            variable="calibration_pinholes_name",
            parameter="name of selected calibration for pinholes",
            value=self.calibration_pinholes["name"],
        )
        interface.results.add_result(
            variable="calibration_pinholes_date",
            parameter="creation date of selected calibration for pinholes",
            value=self.calibration_pinholes["date"],
        )
        interface.results.add_result(
            variable="calibration_pinholes_threshold",
            parameter="threshold of selected calibration for pinholes",
            value=self.calibration_pinholes["threshold"],
        )
        interface.results.add_result(
            variable="calibration_pinholes_parameters",
            parameter="parameters of selected calibration for pinholes",
            value=self.calibration_pinholes["parameters"],
        )
        interface.results.add_result(
            variable="calibration_pinholes_minimum_pixels",
            parameter="minimum size (pixels) of selected calibration for pinholes",
            value=self.calibration_pinholes["minimum_size"],
        )
        interface.results.add_result(
            variable="calibration_pinholes_minimum_size",
            parameter="minimum size (microns) of selected calibration for pinholes",
            value=self.minimum_size_calibration_pinholes,
        )
        interface.results.add_result(
            variable="calibration_pinholes_exposure_time",
            parameter="exposure time used for creating calibration for pinholes",
            value=self.calibration_pinholes["exposure_time"],
        )
        interface.logging.info(
            f"Selected calibration for pinholes'{self.calibration_pinholes['name']}, created on {self.calibration_pinholes['date']}'."
        )
        interface.logging.info(
            f"Minimum pinhole diameter detectable with calibration is {round(self.minimum_size_calibration_pinholes, 1)} µm."
        )
        if self.calibration_pinholes["exposure_time"] != interface.results.ExposureTime["value"]:
            interface.logging.exception(
                f"Calibration is not suitable for photo because of wrong exposure time. Calibration: {self.calibration_pinholes['exposure_time']}, photo: {interface.results.exposure_time['value']}."
            )
            raise Exception(
                f"Calibration is not suitable for photo because of wrong exposure time. Calibration: {self.calibration_pinholes['exposure_time']}, photo: {interface.results.exposure_time['value']}."
            )

    def conv_pixel_diameter(self, x: float) -> float:
        """
        Return diameter based on number of pixels using calibration function
        created using microscopic measurements.

        Args:
            x (float): number of pixels of pinhole

        Returns:
            float: diameter in micrometers
        """
        diameter = (
            self.calibration_pinholes["parameters"][0] * x
            + self.calibration_pinholes["parameters"][1] * x * x
            + self.calibration_pinholes["parameters"][2] * x * x * x
            + self.calibration_pinholes["parameters"][3] * x * x * x * x
        )
        return diameter

    def binarize_photo(self) -> np.ndarray:
        gray_photo = sm.util.img_as_ubyte(sm.color.rgb2gray(self.cropped_photo))
        binarized_photo = (
            gray_photo > self.calibration_pinholes["threshold"]
        ) * self.cropped_mask
        self.binarized_photo = binarized_photo != 0  # make boolean
        interface.logging.info(f"Created binarized (cropped) photo.")
        return self.binarized_photo

    def big_holes(self, photo: np.ndarray) -> np.ndarray:
        big_holes = np.invert(
            sm.morphology.remove_small_holes(
                np.invert(photo),
                area_threshold=self.calibration_pinholes["minimum_size"],
            )
        )
        self.holes = big_holes
        interface.logging.info(
            f"Created black photo with holes bigger than {self.calibration_pinholes['minimum_size']} pixels."
        )
        return self.holes

    def label_holes(self, holes: np.ndarray) -> np.ndarray:
        labels = sm.morphology.label(holes)
        self.labels_holes = labels
        self.no_pinholes = np.max(labels)
        interface.logging.info(f"Labeled {self.no_pinholes} pinholes.")
        return self.labels_holes

    def set_steps(self) -> list:
        try:
            steps = [int(i) for i in PINHOLE_CLASS_STEPS]
            steps.sort()
        except ValueError:
            interface.logging.exception(
                "Pinhole category sizes could not be converted in a sorted list of integers. Please provide a list of integers."
            )
            raise ValueError(
                "Pinhole category sizes could not be converted in a sorted list of integers. Please provide a list of integers."
            )
        if not len(set(steps)) == 4:
            interface.logging.exception(
                f"I need 4 different pinhole category sizes, but found {len(set(steps))}."
            )
            raise ValueError(
                f"I need 4 different pinhole category sizes, but found {len(set(steps))}."
            )
        self.steps = steps
        interface.logging.info(
            f"The pinhole size categories are < {steps[0]} µm, {steps[0]}–{steps[1]} µm, {steps[1]}–{steps[2]} µm, {steps[2]}–{steps[3]} µm, and > {steps[3]} µm."
        )
        return steps

    def extract_pinhole_details(self, labels: np.ndarray) -> list:
        details = []

        def append_details(region, category: int) -> None:
            nonlocal details
            details.append(
                [
                    region.centroid[0],
                    region.centroid[1],
                    number,
                    region.equivalent_diameter,
                    category,
                    region.area,
                    region.solidity,
                    self.conv_pixel_diameter(region.area),
                ]
            )

        number = 1

        for region in sm.measure.regionprops(labels):
            if self.conv_pixel_diameter(region.area) < self.steps[0]:
                append_details(region, 1)
            elif self.conv_pixel_diameter(region.area) < self.steps[1]:
                append_details(region, 2)
            elif self.conv_pixel_diameter(region.area) < self.steps[2]:
                append_details(region, 3)
            elif self.conv_pixel_diameter(region.area) < self.steps[3]:
                append_details(region, 4)
            else:
                append_details(region, 5)
            number += 1
        self.details = details
        interface.logging.info(f"Extracted details for {len(self.details)} pinholes.")
        return self.details

    def save_pinhole_details(self, details: list) -> None:
        with open(
            f"{os.path.splitext(self.photo_path)[0]}_pinholes.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            for i in details:
                writer.writerow(
                    [self.sample_name, i[2], i[0], i[1], i[3], i[4], i[5], i[6], i[7]]
                )
        interface.logging.info(
            f"Saved CSV file with pinhole data to {os.path.splitext(self.photo_path)[0]}_pinholes.csv."
        )

    def create_circled_photo(
        self, binarized_photo: np.ndarray, labels: np.ndarray
    ) -> np.ndarray:
        markings_cat1 = np.zeros((binarized_photo.shape[0], binarized_photo.shape[1]))
        markings_cat2 = markings_cat1.copy()
        markings_cat3 = markings_cat1.copy()
        markings_cat4 = markings_cat1.copy()
        markings_cat5 = markings_cat1.copy()

        number = 1

        for region in sm.measure.regionprops(labels):
            rc, cc = sm.draw.circle_perimeter(
                round(region.centroid[0]),
                round(region.centroid[1]),
                round(region.equivalent_diameter) * 2,
                shape=(binarized_photo.shape[0], binarized_photo.shape[1]),
            )
            if self.conv_pixel_diameter(region.area) < self.steps[0]:
                markings_cat1[rc, cc] = 1
            elif self.conv_pixel_diameter(region.area) < self.steps[1]:
                markings_cat2[rc, cc] = 1
            elif self.conv_pixel_diameter(region.area) < self.steps[2]:
                markings_cat3[rc, cc] = 1
            elif self.conv_pixel_diameter(region.area) < self.steps[3]:
                markings_cat4[rc, cc] = 1
            else:
                markings_cat5[rc, cc] = 1
            number += 1

        markings_cat3 = sm.morphology.dilation(
            markings_cat3, sm.morphology.disk(radius=2)
        )
        markings_cat4 = sm.morphology.dilation(
            markings_cat4, sm.morphology.disk(radius=2)
        )
        markings_cat5 = sm.morphology.dilation(
            markings_cat5, sm.morphology.disk(radius=2)
        )

        self.circled_photo = sm.img_as_ubyte(self.cropped_photo.copy())
        self.circled_photo[markings_cat1 == 1] = [255, 0, 0]
        self.circled_photo[markings_cat2 == 1] = [0, 0, 255]
        self.circled_photo[markings_cat3 == 1] = [0, 255, 0]
        self.circled_photo[markings_cat4 == 1] = [255, 255, 0]
        self.circled_photo[markings_cat5 == 1] = [255, 255, 255]
        interface.logging.info(f"Created photo with circled pinholes.")
        return self.circled_photo

    def save_labeled_photo(
        self, circled_photo: np.ndarray, details: list
    ) -> np.ndarray:
        plt.clf()
        img = self.circled_photo.copy()
        for i in details:
            if i[4] == 1:
                plt.text(
                    i[1],
                    i[0] - i[3] * 4,
                    f"{i[2]} ({round(i[7])} \u03bcm)",
                    dict(color="red", va="center", ha="center", fontsize=1 + i[3] / 3),
                )
            if i[4] == 2:
                plt.text(
                    i[1],
                    i[0] - i[3] * 4,
                    f"{i[2]} ({round(i[7])} \u03bcm)",
                    dict(color="blue", va="center", ha="center", fontsize=1 + i[3] / 3),
                )
            if i[4] == 3:
                plt.text(
                    i[1],
                    i[0] - i[3] * 4,
                    f"{i[2]} ({round(i[7])} \u03bcm)",
                    dict(
                        color="green", va="center", ha="center", fontsize=1 + i[3] / 3
                    ),
                )
            if i[4] == 4:
                plt.text(
                    i[1],
                    i[0] - i[3] * 4,
                    f"{i[2]} ({round(i[7])} \u03bcm)",
                    dict(
                        color="yellow", va="center", ha="center", fontsize=1 + i[3] / 3
                    ),
                )
            if i[4] == 5:
                plt.text(
                    i[1],
                    i[0] - i[3] * 4,
                    f"{i[2]} ({round(i[7])} \u03bcm)",
                    dict(
                        color="white", va="center", ha="center", fontsize=1 + i[3] / 3
                    ),
                )
        plt.axis("off")
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.imshow(img)
        try:
            plt.savefig(
                os.path.splitext(self.photo_path)[0] + "_pinholes.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=450,
            )
            interface.logging.info(
                f"Saved photo with marked and labeled pinholes to {os.path.splitext(self.photo_path)[0]}_pinholes.png."
            )
        except:
            logging.interface.exception(
                f"Photo with marked and labeled pinholes could not be saved to {os.path.splitext(self.photo_path)[0]}_pinholes.png."
            )
            raise Exception(
                f"Photo with marked and labeled pinholes could not be saved to {os.path.splitext(self.photo_path)[0]}_pinholes.png."
            )


def run_pinholes():
    pinholer = Pinholer(photo.photo)
    pinholer.set_steps()
    binarized = pinholer.binarize_photo()
    holes = pinholer.big_holes(binarized)
    pinholer.save_image(pinholer.holes, "holes")
    labels = pinholer.label_holes(holes)
    pinholer.save_image(pinholer.labels_holes, "labels")
    details = pinholer.extract_pinhole_details(labels)
    pinholer.save_pinhole_details(details)
    circled_photo = pinholer.create_circled_photo(binarized, labels)
    pinholer.save_image(pinholer.circled_photo, "circled")
    pinholer.save_labeled_photo(circled_photo, details)

    print("\a")


# ------------------------------------------------
# executions

is_main = __name__ == "__main__"

if is_main:
    interface.run_interface()
    photo.run_photo()
    run_pinholes()
