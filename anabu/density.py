#!/usr/bin/env python3

"""
Density/brightness evaluator
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

import numpy as np
import scipy.stats
import skimage as sm

# ------------------------------------------------
# variables

# calibration for brightness/optical density
CALIBRATION_A = {
    "name": "Calibration A",
    "date": "2023-02-22",
    "parameters": [
        (254.99999999999986, 0.0),
        (254.97884214253884, 2.144),
        (179.62991560227036, 3.321),
        (100.3155623762223, 3.808),
        (83.99359301605978, 3.918),
        (82.15923041283685, 3.947),
        (39.96343977596004, 4.422),
        (36.24442322391781, 4.435),
        (29.2106679282811, 4.495),
        (26.473770420634942, 4.615),
        (26.335230269520142, 4.645),
        (24.72575704825937, 4.666),
        (24.182287446540485, 4.669),
        (20.817865606171484, 4.754),
        (16.954580589831643, 4.8),
        (4.681635540516993, 5.305),
        (1.9584211906741886, 5.7),
    ],
    "exposure_time": 30.0,
}

# ------------------------------------------------
# function/class definitions


class Evaluator:
    def __init__(self, photo: photo.Photo) -> None:
        attributes_inherit = {
            "sample_name",
            "cropped_photo",
            "cropped_mask",
            "photo_path",
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
                    f"Attribute {attr} missing in {photo}. Cannot initiate Evaluator object."
                )
                raise Exception(
                    f"Attribute {attr} missing in {photo}. Cannot initiate Evaluator object."
                )
        interface.logging.info(f"Initiated Evaluator object for {self.sample_name}.")
        self.calibration_density = CALIBRATION_A
        interface.results.add_result(
            variable="calibration_density_name",
            parameter="name of selected calibration for optical density",
            value=self.calibration_density["name"],
        )
        interface.results.add_result(
            variable="calibration_density_date",
            parameter="creation date of selected calibration for optical density",
            value=self.calibration_density["date"],
        )
        interface.results.add_result(
            variable="calibration_density_parameters",
            parameter="parameters of selected calibration for optical density",
            value=self.calibration_density["parameters"],
        )
        interface.results.add_result(
            variable="calibration_density_exposure_time",
            parameter="exposure time used for creating calibration for optical density",
            value=self.calibration_density["exposure_time"],
        )
        interface.logging.info(
            f'Selected calibration for optical density "{self.calibration_density["name"]}", created on {self.calibration_density["date"]}.'
        )
        if (
            self.calibration_density["exposure_time"]
            != interface.results.ExposureTime["value"]
        ):
            interface.logging.exception(
                f"Calibration is not suitable for photo because of wrong exposure time. Calibration: {self.calibration_density['exposure_time']}, photo: {interface.results.ExposureTime['value']}."
            )
            raise Exception(
                f"Calibration is not suitable for photo because of wrong exposure time. Calibration: {self.calibration_density['exposure_time']}, photo: {interface.results.ExposureTime['value']}."
            )

    def create_grey_photo(self) -> np.ndarray:
        self.grey_photo = sm.util.img_as_ubyte(sm.color.rgb2gray(self.cropped_photo))
        interface.logging.info(f"Created 8-bit image.")
        return self.grey_photo

    def create_brightness_arrays(self) -> None:
        self.number_total_pixels = np.count_nonzero(
            np.invert(np.isnan(self.grey_photo)) * self.cropped_mask
        )
        interface.results.add_result(
            variable="number_pixels",
            parameter="number of pixels in evaluation",
            value=self.number_total_pixels,
        )
        interface.logging.info(
            f"The nonmasked area contains {self.number_total_pixels} pixels which will be evaluated."
        )
        self.brightness_array = np.linspace(0, 255, 256).astype(int)
        self.brightness_counts = np.array(
            [
                np.count_nonzero((self.grey_photo == i) * self.cropped_mask)
                for i in self.brightness_array
            ]
        )
        assert np.sum(self.brightness_counts) == self.number_total_pixels
        assert len(self.brightness_counts) == 256
        self.brightness_fraction = self.brightness_counts / self.number_total_pixels
        assert round(np.sum(self.brightness_fraction), 10) == 1
        self.brightness_cumulative = np.array(
            [
                np.count_nonzero((self.grey_photo < i + 1) * self.cropped_mask)
                for i in self.brightness_array
            ]
        )
        assert self.brightness_cumulative[-1] == self.number_total_pixels
        self.cumulative_fraction = self.brightness_cumulative / self.number_total_pixels
        assert self.cumulative_fraction[-1] == 1
        self.brightness_percentage = (
            self.brightness_counts / self.number_total_pixels * 100
        )
        self.cumulative_percentage = (
            self.brightness_cumulative / self.number_total_pixels * 100
        )
        interface.logging.info("Calculated brightness distributions.")

    def export_distributions(self) -> None:
        if interface.user_settings.export_distribution["value"] == False:
            return None
        distributions_list = [
            ["sample name", "ExpTime", "FNumb", "brightness", "intensity_counts"]
        ]
        for value in range(len(self.brightness_array)):
            distributions_list.append(
                [
                    self.sample_name,
                    interface.results.ExposureTime["value"],
                    interface.results.FNumber["value"],
                    self.brightness_array[value],
                    self.brightness_counts[value],
                ]
            )
        with open(
            f"{os.path.splitext(self.photo_path)[0]}_distribution.csv",
            "w",
            encoding="UTF8",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerows(distributions_list)
        interface.logging.info(
            f"Exported file with distributions: {os.path.splitext(self.photo_path)[0]}_distribution.csv"
        )

    def calculate_distribution_params(self) -> None:
        def mean_2(array: np.ndarray) -> float:
            """
            Returns a weighted average value for an array, equivalent to M_w is polymer science.
            It's assumed that the values in the array are counts for brightness values 0, 1, 2, 3, ...
            """
            sum1, sum2 = 0, 0
            for x in range(len(array)):
                sum1 = sum1 + array[x] * x
                sum2 = sum2 + array[x] * x * x
            return sum2 / sum1

        def mean_3(array: np.ndarray) -> float:
            """
            Returns a weighted average value for an array, equivalent to M_z is polymer science.
            It's assumed that the values in the array are counts for brightness values 0, 1, 2, 3, ...
            """
            sum2, sum3 = 0, 0
            for x in range(len(array)):
                sum2 = sum2 + array[x] * x * x
                sum3 = sum3 + array[x] * x * x * x
            return sum3 / sum2

        def mean_1_4(array: np.ndarray) -> float:
            sum1, sum2 = 0, 0
            for x in range(len(array)):
                sum1 = sum1 + array[x] * (x**0.4)
                sum2 = sum2 + array[x] * (x**1.4)
            return sum2 / sum1

        self.brightness_min = np.min(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The minimum brightness value is {self.brightness_min}."
        )
        interface.results.add_result(
            variable="brightness_min",
            parameter="minimum brightness value",
            value=self.brightness_min,
        )
        self.brightness_max = np.max(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The maximum brightness value is {self.brightness_max}."
        )
        interface.results.add_result(
            variable="brightness_max",
            parameter="maximum brightness value",
            value=self.brightness_max,
        )
        self.brightness_peak = int(
            np.where(self.brightness_counts == np.amax(self.brightness_counts))[0]
        )
        # FIXME Implement better solution for possibility that two values have the same brightness.
        interface.logging.info(
            f"The most often found brightness value is {self.brightness_peak}."
        )
        interface.results.add_result(
            variable="brightness_peak",
            parameter="most found brightness value",
            value=self.brightness_peak,
        )
        self.brightness_mean = np.mean(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The average brightness value is {round(self.brightness_mean,2)}."
        )
        interface.results.add_result(
            variable="brightness_mean",
            parameter="mean brightness value",
            value=self.brightness_mean,
        )
        self.brightness_25 = np.percentile(self.grey_photo[self.cropped_mask], 25)
        interface.logging.info(
            f"The 25th brightness percentile is {self.brightness_25}."
        )
        interface.results.add_result(
            variable="brightness_25",
            parameter="25th brightness percentile",
            value=self.brightness_25,
        )
        self.brightness_median = np.median(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The median brightness value is {self.brightness_median}."
        )
        interface.results.add_result(
            variable="brightness_median",
            parameter="median brightness value",
            value=self.brightness_median,
        )
        self.brightness_75 = np.percentile(self.grey_photo[self.cropped_mask], 75)
        interface.logging.info(
            f"The 25th brightness percentile is {self.brightness_75}."
        )
        interface.results.add_result(
            variable="brightness_75",
            parameter="25th brightness percentile",
            value=self.brightness_75,
        )
        self.brightness_variance = np.var(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The variance of the brightness distribution is {round(self.brightness_variance,2)}."
        )
        interface.results.add_result(
            variable="brightness_variance",
            parameter="variance of brightness distribution",
            value=self.brightness_variance,
        )
        self.brightness_stdev = np.std(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The standard deviation of the brightness distribution is {round(self.brightness_stdev,2)}."
        )
        interface.results.add_result(
            variable="brightness_stdev",
            parameter="standard deviation of brightness distribution",
            value=self.brightness_stdev,
        )
        self.brightness_skew = scipy.stats.skew(self.grey_photo[self.cropped_mask])
        interface.logging.info(
            f"The skew of the brightness distribution is {round(self.brightness_skew,2)}."
        )
        interface.results.add_result(
            variable="brightness_skew",
            parameter="skew of brightness distribution",
            value=self.brightness_skew,
        )
        self.brightness_kurtosis = scipy.stats.kurtosis(
            self.grey_photo[self.cropped_mask]
        )
        interface.logging.info(
            f"The kurtosis of the brightness distribution is {round(self.brightness_kurtosis,2)}."
        )
        interface.results.add_result(
            variable="brightness_kurtosis",
            parameter="kurtosis of brightness distribution",
            value=self.brightness_kurtosis,
        )
        self.brightness_weighted_mean = mean_2(self.brightness_fraction)
        interface.logging.info(
            f"The brightness-weighted mean of the brightness distribution is {round(self.brightness_weighted_mean,2)}."
        )
        interface.results.add_result(
            variable="brightness_weighted_mean",
            parameter="brightness-weighted mean of brightness distribution",
            value=self.brightness_weighted_mean,
        )
        self.brightness_2_weighted_mean = mean_3(self.brightness_fraction)
        interface.logging.info(
            f"The brightness-squared-weighted mean of the brightness distribution is {round(self.brightness_2_weighted_mean,2)}."
        )
        interface.results.add_result(
            variable="brightness_2_weighted_mean",
            parameter="brightness-squared weighted mean of brightness distribution",
            value=self.brightness_2_weighted_mean,
        )
        self.brightness_1_4_weighted_mean = mean_1_4(self.brightness_fraction)
        interface.logging.info(
            f"The brightness-weighted mean (1.4) of the brightness distribution is {round(self.brightness_1_4_weighted_mean,2)}."
        )
        interface.results.add_result(
            variable="brightness_1_4_weighted_mean",
            parameter="brightness-1.4 weighted mean of brightness distribution",
            value=self.brightness_1_4_weighted_mean,
        )
        self.brightness_dispersity = (
            self.brightness_weighted_mean / self.brightness_mean
        )
        interface.logging.info(
            f"The dispersity of the brightness distribution is {round(self.brightness_dispersity,2)}."
        )
        interface.results.add_result(
            variable="brightness_dispersity",
            parameter="dispersity of brightness distribution",
            value=self.brightness_dispersity,
        )
        for threshold in [99, 95, 90, 75, 50, 25, 10, 2, 1, 0.5, 0.25, 0.1]:
            interface.logging.info(
                f"Just over {str(threshold)}% of pixels have a brightness of at least\t {str(np.where((self.cumulative_percentage) >= threshold)[0][0])}."
            )
            interface.results.add_result(
                variable=f"brightness_{threshold}",
                parameter=f"brightness which {threshold}% of pixels have at least",
                value=np.where((self.cumulative_percentage) >= threshold)[0][0],
            )

    def calculate_OD(self) -> float:
        if (
            self.brightness_1_4_weighted_mean
            > self.calibration_density["parameters"][0][0]
        ):
            print(
                "Sample is brighter than brightest calibration sample. Cannot convert to optical density."
            )
            return None
        if (
            self.brightness_1_4_weighted_mean
            < self.calibration_density["parameters"][-1][0]
        ):
            print(
                "Sample is darker than darkest calibration sample. Cannot convert to optical density."
            )
            return None
        for i in range(len(self.calibration_density["parameters"])):
            if (
                self.brightness_1_4_weighted_mean
                == self.calibration_density["parameters"][i][0]
            ):
                optical_density = self.calibration_density["parameters"][i][1]
                self.optical_density = round(optical_density, 3)
                interface.results.add_result(
                    variable="optical_density",
                    parameter="average optical density of sample",
                    value=self.optical_density,
                )
                interface.logging.info(
                    f"The average optical density of the sample is {self.optical_density}"
                )
                return self.optical_density
        index_above = min(
            range(len(self.calibration_density["parameters"])),
            key=lambda x: self.calibration_density["parameters"][x][0]
            - self.brightness_1_4_weighted_mean
            if self.calibration_density["parameters"][x][0]
            - self.brightness_1_4_weighted_mean
            > 0
            else 256,
        )
        index_below = min(
            range(len(self.calibration_density["parameters"])),
            key=lambda x: self.brightness_1_4_weighted_mean
            - self.calibration_density["parameters"][x][0]
            if self.brightness_1_4_weighted_mean
            - self.calibration_density["parameters"][x][0]
            > 0
            else 256,
        )
        assert index_above == index_below - 1
        optical_density = self.calibration_density["parameters"][index_above][1] - (
            self.calibration_density["parameters"][index_above][0]
            - self.brightness_1_4_weighted_mean
        ) / (
            self.calibration_density["parameters"][index_above][0]
            - self.calibration_density["parameters"][index_below][0]
        ) * (
            self.calibration_density["parameters"][index_above][1]
            - self.calibration_density["parameters"][index_below][1]
        )
        self.optical_density = round(optical_density, 3)
        interface.results.add_result(
            variable="optical_density",
            parameter="average optical density of sample",
            value=self.optical_density,
        )
        interface.logging.info(
            f"The average optical density of the sample is {self.optical_density}"
        )
        return self.optical_density


def run_density():
    global evaluator
    evaluator = Evaluator(photo.photo)
    interface.Gui.update_progress_bar()
    evaluator.create_grey_photo()
    interface.Gui.update_progress_bar()
    evaluator.create_brightness_arrays()
    interface.Gui.update_progress_bar()
    evaluator.calculate_distribution_params()
    interface.Gui.update_progress_bar()
    evaluator.calculate_OD()
    interface.Gui.update_progress_bar()
    evaluator.export_distributions()
    interface.Gui.update_progress_bar()


# ------------------------------------------------
# executions

is_main = __name__ == "__main__"

if is_main:
    interface.run_interface()
    photo.run_photo()
    run_density()
