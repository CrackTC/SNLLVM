import os
import sys
from LL1 import LL1
from LexicalaAnalyzer import lex

from SemanticAnalysis import semantic

gram_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "./data/grammar.txt"
)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py [lex] [parse] [semantic] <input>")
        exit(-1)

    input = sys.argv[-1]
    fnameNoExt, _ = os.path.splitext(input)

    outputNames = {
        "lex": fnameNoExt + ".tk",
        "parse": fnameNoExt + ".ast",
        "semantic": fnameNoExt + ".sem",
    }

    idx = 1
    if sys.argv[idx] == "lex":
        idx += 1
        try:
            if lex(input, outputNames["lex"]) != 0:
                print("Lexical analysis failed")
                exit(-1)
        except:
            print("Lexical analysis failed")
            exit(-1)
    if sys.argv[idx] == "parse":
        idx += 1
        try:
            ll1 = LL1(gram_path, outputNames["lex"], outputNames["parse"])
            ll1.run()
            err, _ = ll1.showError(verbose=True)
            if err != 0:
                print("Gramma analysis failed")
                exit(-1)
        except:
            print("Gramma analysis failed")
            exit(-1)
    if sys.argv[idx] == "semantic":
        idx += 1
        try:
            if semantic(outputNames["parse"], outputNames["semantic"]) != 0:
                print("Semantic analysis failed")
                exit(-1)
        except:
            print("Semantic analysis failed")
            exit(-1)
