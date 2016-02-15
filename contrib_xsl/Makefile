XSLTPROC = xsltproc
CDDIR    = ../../client-data
HELPDIR  = help

about-server:
	@mkdir -p $(CDDIR)/$(HELPDIR)
	@$(XSLTPROC) about-server.xsl $(CDDIR)/contributors.xml > $(CDDIR)/$(HELPDIR)/about-server.txt
	@echo "The file about-server.txt was created successfully."
