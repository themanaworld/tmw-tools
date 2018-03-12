XSLTPROC = xsltproc
CDDIR	= ../../client-data
WKDIR	= ../../wiki
HELPDIR = help

all: about-server wiki

about-server:
	@mkdir -p $(CDDIR)/$(HELPDIR)
	@$(XSLTPROC) -o $(CDDIR)/$(HELPDIR)/about-server.txt about-server.xsl contributors.xml 
	@echo "The file about-server.txt was created successfully."

wiki:
	@$(XSLTPROC) wiki.xsl contributors.xml > $(WKDIR)/Contributors.md
	@echo "Wiki generated"
