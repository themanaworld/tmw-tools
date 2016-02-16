XSLTPROC = xsltproc
CDDIR    = ../../client-data
HELPDIR  = help

all: about-server wiki

about-server:
	@mkdir -p $(CDDIR)/$(HELPDIR)
	@$(XSLTPROC) -o $(CDDIR)/$(HELPDIR)/about-server.txt about-server.xsl contributors.xml 
	@echo "The file about-server.txt was created successfully."

wiki:
	@$(XSLTPROC) wiki.xsl contributors.xml | less
	@echo "You can now place this output in: http://wiki.evolonline.org/contributors"
