R = ..
PY = $(shell find $(R)/python -name '*.py')
TOP = $(addprefix $(R)/,Makefile env.sh)

.PHONY:all
all: report.ipynb

report.ipynb: report.md $(PY) $(TOP)
	pandoc -f markdown+native_divs report.md -o report.ipynb


