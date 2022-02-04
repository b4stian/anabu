#!/usr/bin/env python3

# ------------------------------------------------
# imports

from pptx import Presentation
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT

# ------------------------------------------------
# variables

path_master_ppt = r"ppt/PPT_master.pptx"
# This module will fail if wrong PPT_master is used.

# ------------------------------------------------
# functions/classes

# ------------------------------------------------
# executions

prs = Presentation(path_master_ppt)

title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title_slide.placeholders[0].text = "[Sample name]"
title_slide.placeholders[13].text = "Evaluation results for light table photo"

# TODO change to target folder
prs.save(r"test_photos/anabu_results.pptx")
