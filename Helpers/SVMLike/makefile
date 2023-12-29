#https://makefiletutorial.com/
#https://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/
#makes a dynamic library when termnal at this location runs 'make'
IDIR =include
ODIR =obj
BIN =bin
SDIR=source

classes=Model SVMLike1

DEPS = $(patsubst %,$(IDIR)/%.hpp,$(classes))
SRC = $(patsubst %,$(SDIR)/%.cpp,$(classes))
OBJ = $(patsubst %,$(ODIR)/%.o,$(classes))
newSO=$(BIN)/SVMLike.so

CFLAGS=-I$(IDIR) -fPIC -Werror
CC="/usr/bin/g++-11"

$(BIN)/SVMLike.so:$(ODIR)/Model.o $(ODIR)/SVMLike1.o
	@echo SVMLike link
	$(CC) -shared -o $(BIN)/SVMLike.so $(ODIR)/Model.o $(ODIR)/SVMLike1.o

$(ODIR)/Model.o: $(SDIR)/Model.cpp $(IDIR)/Model.hpp
	@echo Model compile
	$(CC) $(CFLAGS) -c $(SDIR)/Model.cpp -o $(ODIR)/Model.o

$(ODIR)/SVMLike1.o: $(SDIR)/SVMLike1.cpp $(IDIR)/SVMLike1.hpp $(IDIR)/Model.hpp
	@echo SVMLike1 compile
	$(CC) $(CFLAGS) -c $(SDIR)/SVMLike1.cpp -o $(ODIR)/SVMLike1.o

clean:
	rm -f $(BIN)/SVMLike.so
	rm -f $(ODIR)/Model.o
	rm -f $(ODIR)/SVMLike1.o