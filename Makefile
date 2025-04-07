.PHONY: all

TEX = $(shell find tex -name '[^_]*.tex')
PDF = report.pdf

.PHONY: all $(PDF)
all: $(PDF)

$(PDF):
	$(MAKE) -C tex $(notdir $@)

$(DEP):
	-$(MAKE) -p -C tex $(notdir $@)

.PHONY:help
help:
	$(MAKE) -C tex help

