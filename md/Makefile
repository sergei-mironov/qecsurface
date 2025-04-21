R = ..
PY = $(shell find $(R)/python -name '*.py')

.PHONY:all
all:report.ipynb

report.ipynb: report.md $(PY)
	pandoc -f markdown+native_divs report.md -o report.ipynb


