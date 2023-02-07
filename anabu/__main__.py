#!/usr/bin/env python3

try:
    from anabu.analysis import run_analysis_photo
except:
    from analysis import run

# ------------------------------------------------
# executions

is_main = __name__ == "__main__"

if is_main:
    run_analysis_photo()
