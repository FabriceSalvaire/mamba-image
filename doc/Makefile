all: docs

DOCS = $(shell ls -d */)

clean:
	rm -f *~ *.pdf
	@for dir in $(DOCS); do \
		(cd $$dir; ${MAKE} clean); \
	done

docs: 
	@for dir in $(DOCS); do \
		(cd $$dir; ${MAKE}); \
	done
	
