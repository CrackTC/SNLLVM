SNL_SRC := test/bubble/bubble.snl
SRC_BASE := $(basename $(notdir $(SNL_SRC)))
SRC_DIR := $(dir $(SNL_SRC))

compile: build/Sorac.SNL
	python preprocess/main.py lex parse semantic $(SNL_SRC)
	build/Sorac.SNL $(basename $(SNL_SRC)).ast

test: compile
	cat $(SRC_DIR)input | Mars nc db $(SRC_BASE).s >output 2>/dev/null
	diff $(SRC_DIR)ans output

build/Sorac.SNL: codegen/Sorac.SNL.csproj $(shell find codegen -type f -name '*.cs') $(shell find codegen/Bootstrap -type f -name '*.s')
	dotnet publish -c Release codegen/Sorac.SNL.csproj -o build

clean:
	rm -rf build
	find -name '*.ast' -delete
	find -name '*.tk' -delete
	find -name '*.sem' -delete

.PHONY: clean compile test
