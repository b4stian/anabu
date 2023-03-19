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

    @staticmethod
    def mean_1_4(array: np.ndarray) -> float:
        sum1, sum2 = 0, 0
        for x in range(len(array)):
            sum1 = sum1 + array[x] * (x**0.4)
            sum2 = sum2 + array[x] * (x**1.4)
        return sum2 / sum1

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
        self.brightness_1_4_weighted_mean = self.mean_1_4(self.brightness_fraction)
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

    def convert_OD(self, weighted_mean: float) -> float:
        if weighted_mean > self.calibration_density["parameters"][0][0]:
            interface.logging.info(
                "Area is brighter than brightest calibration sample. Cannot convert to optical density."
            )
            return None
        if weighted_mean < self.calibration_density["parameters"][-1][0]:
            interface.logging.info(
                "Area is darker than darkest calibration sample. Cannot convert to optical density."
            )
            return None
        for i in range(len(self.calibration_density["parameters"])):
            if weighted_mean == self.calibration_density["parameters"][i][0]:
                optical_density = self.calibration_density["parameters"][i][1]
                return round(optical_density, 3)
        index_above = min(
            range(len(self.calibration_density["parameters"])),
            key=lambda x: self.calibration_density["parameters"][x][0] - weighted_mean
            if self.calibration_density["parameters"][x][0] - weighted_mean > 0
            else 256,
        )
        index_below = min(
            range(len(self.calibration_density["parameters"])),
            key=lambda x: weighted_mean - self.calibration_density["parameters"][x][0]
            if weighted_mean - self.calibration_density["parameters"][x][0] > 0
            else 256,
        )
        assert index_above == index_below - 1
        optical_density = self.calibration_density["parameters"][index_above][1] - (
            self.calibration_density["parameters"][index_above][0] - weighted_mean
        ) / (
            self.calibration_density["parameters"][index_above][0]
            - self.calibration_density["parameters"][index_below][0]
        ) * (
            self.calibration_density["parameters"][index_above][1]
            - self.calibration_density["parameters"][index_below][1]
        )
        return round(optical_density, 3)

    def calculate_OD(self) -> None:
        self.optical_density = self.convert_OD(self.brightness_1_4_weighted_mean)
        interface.logging.info(
            f"The average optical density of the sample is {self.optical_density}."
        )
        interface.results.add_result(
            variable="optical_density",
            parameter="average optical density of sample",
            value=self.optical_density,
        )
        disk_radius = int(
            photo.SCALE_FACTOR * interface.user_settings.radius_min_max["value"]
        )
        if hasattr(photo.photo, "masked_cropped_photo"):
            img = photo.photo.masked_cropped_photo.copy()
        else:
            img = photo.photo.photo.copy()
        disk_min_rr, disk_min_cc = sm.draw.disk(
            self.ind_min, disk_radius, shape=img.shape
        )
        disk_max_rr, disk_max_cc = sm.draw.disk(
            self.ind_max, disk_radius, shape=img.shape
        )
        grey = sm.util.img_as_ubyte(sm.color.rgb2gray(img.copy()))
        brightness_counts_min = np.array(
            [
                np.count_nonzero(grey[disk_min_rr, disk_min_cc] == i)
                for i in self.brightness_array
            ]
        )
        assert np.sum(brightness_counts_min) == np.count_nonzero(
            grey[disk_min_rr, disk_min_cc]
        )
        brightness_fraction_min = brightness_counts_min / np.count_nonzero(
            grey[disk_min_rr, disk_min_cc]
        )
        assert round(np.sum(brightness_fraction_min), 10) == 1
        self.OD_min = self.convert_OD(self.mean_1_4(brightness_fraction_min))
        interface.logging.info(
            f"The brightest circle has an optical density of {self.OD_min}."
        )
        interface.results.add_result(
            variable="optical_density_min",
            parameter="optical density of brightest circle",
            value=self.OD_min,
        )
        brightness_counts_max = np.array(
            [
                np.count_nonzero(grey[disk_max_rr, disk_max_cc] == i)
                for i in self.brightness_array
            ]
        )
        assert np.sum(brightness_counts_max) == np.count_nonzero(
            grey[disk_max_rr, disk_max_cc]
        )
        brightness_fraction_max = brightness_counts_max / np.count_nonzero(
            grey[disk_max_rr, disk_max_cc]
        )
        assert round(np.sum(brightness_fraction_max), 10) == 1
        self.OD_max = self.convert_OD(self.mean_1_4(brightness_fraction_max))
        interface.logging.info(
            f"The darkest circle has an optical density of {self.OD_max}."
        )
        interface.results.add_result(
            variable="optical_density_max",
            parameter="optical density of brightest circle",
            value=self.OD_max,
        )

    def min_max_density_centers(self) -> tuple:
        def mean_brightness_circle(
            grey_photo: np.ndarray, disk_radius: float
        ) -> np.ndarray:
            disk = sm.morphology.disk(int(photo.SCALE_FACTOR * disk_radius))
            return sm.filters.rank.mean(grey_photo, disk)

        if hasattr(photo.photo, "masked_cropped_photo"):
            img = photo.photo.masked_cropped_photo.copy()
            interface.logging.info("Finding min/max circle on cropped photo.")
        else:
            img = photo.photo.photo.copy()
            interface.logging.info("Finding min/max circle on original photo.")
        disk_radius = int(
            photo.SCALE_FACTOR * interface.user_settings.radius_min_max["value"]
        )
        grey = sm.util.img_as_ubyte(sm.color.rgb2gray(img.copy()))
        avg = mean_brightness_circle(
            grey, interface.user_settings.radius_min_max["value"]
        )
        mask_eroded = photo.photo.cropped_mask.copy()
        disk = sm.morphology.disk(disk_radius)
        mask_eroded = sm.morphology.binary_erosion(mask_eroded, footprint=disk)
        avg_eroded_min = avg.copy()
        avg_eroded_min[~mask_eroded] = 0
        avg_eroded_max = avg.copy()
        avg_eroded_max[~mask_eroded] = 255
        ind_min = np.unravel_index(
            np.argmax(avg_eroded_min, axis=None), avg_eroded_min.shape
        )
        self.ind_min = ind_min
        interface.results.add_result(
            variable="center_min_circle",
            parameter="center point of the circle with maximum brightness",
            value=ind_min,
        )
        ind_max = np.unravel_index(
            np.argmin(avg_eroded_max, axis=None), avg_eroded_max.shape
        )
        self.ind_max = ind_max
        interface.results.add_result(
            variable="center_max_circle",
            parameter="center point of the circle with minimum brightness",
            value=ind_max,
        )
        if hasattr(photo.photo, "masked_cropped_photo"):
            interface.logging.info(
                f'The center of the circle ({interface.user_settings.radius_min_max["value"]*2} mm diameter) with maximum brightness is at pixel {ind_min} in the cropped photo.'
            )
            interface.logging.info(
                f'The center of the circle ({interface.user_settings.radius_min_max["value"]*2} mm diameter) with minimum brightness is at pixel {ind_max} in the cropped photo.'
            )
        else:
            interface.logging.info(
                f'The center of the circle ({interface.user_settings.radius_min_max["value"]*2} mm diameter) with maximum brightness is at pixel {ind_min} in the original photo.'
            )
            interface.logging.info(
                f'The center of the circle ({interface.user_settings.radius_min_max["value"]*2} mm diameter) with minimum brightness is at pixel {ind_max} in the original photo.'
            )
        return ind_max, ind_min

    def draw_min_max_circles(self, ind_min: tuple, ind_max: tuple):
        if hasattr(photo.photo, "masked_cropped_photo"):
            img = photo.photo.masked_cropped_photo.copy()
            interface.logging.info("Drawing min/max circle on cropped photo.")
        else:
            img = photo.photo.photo.copy()
            interface.logging.info("Drawing min/max circle on original photo.")
        disk_radius = int(
            photo.SCALE_FACTOR * interface.user_settings.radius_min_max["value"]
        )
        for i in {1, 2, 3, 4, 5, 6}:
            rrminp, ccminp = sm.draw.circle_perimeter(
                *ind_min, radius=int(disk_radius) + i, method="andres", shape=img.shape
            )
            rrmaxp, ccmaxp = sm.draw.circle_perimeter(
                *ind_max, radius=int(disk_radius) + i, method="andres", shape=img.shape
            )
            if i % 2 == 1:
                img[rrminp, ccminp, :] = [1, 1, 1]
                img[rrmaxp, ccmaxp, :] = [1, 1, 1]
            elif i % 2 == 0:
                img[rrminp, ccminp, :] = [217 / 255, 71 / 255, 95 / 255]
                img[rrmaxp, ccmaxp, :] = [117 / 255, 185 / 255, 108 / 255]
        sm.io.imsave(
            os.path.splitext(self.photo_path)[0] + "_" + "minmax" + ".png",
            sm.util.img_as_ubyte(img),
        )
        photo.photo.cropped_photo = img
        interface.logging.info(
            f'Saved photo with marked min/max brightness circles to {os.path.splitext(self.photo_path)[0] + "_" + "minmax" + ".png"}.'
        )


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
    evaluator.min_max_density_centers()
    interface.Gui.update_progress_bar()
    evaluator.draw_min_max_circles(evaluator.ind_min, evaluator.ind_max)
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
