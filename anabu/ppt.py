#!/usr/bin/env python3

# ------------------------------------------------
# imports

from pptx import Presentation
from pptx.enum.text import PP_ALIGN

# ------------------------------------------------
# executions

prs = Presentation(r"ppt/PPT_master.pptx")

title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title_slide.placeholders[0].text = "[Sample name]"
title_slide.placeholders[13].text = "Evaluation results for light table photo"

prs.save(r"test_photos/anabu_results.pptx")
