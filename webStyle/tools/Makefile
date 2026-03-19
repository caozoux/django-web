CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -lpng

TARGET = png_to_text
SRC = png_to_text.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGET)
