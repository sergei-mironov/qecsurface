.PHONY: all

TEX = $(shell find tex -name '[^_]*.tex')
PDF = tex/report.pdf
IPYNB = md/report.ipynb

.PHONY: all $(PDF) $(IPYNB)
all: $(PDF) $(IPYNB)

$(PDF):
	$(MAKE) -C tex $(notdir $@)

$(IPYNB):
	$(MAKE) -C md $(notdir $@)

.PHONY:help
help:
	$(MAKE) -C tex help

