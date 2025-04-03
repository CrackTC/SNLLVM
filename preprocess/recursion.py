from GrammarError import dealError
from GrammarProcess import predict1
from SyntaxTree import Stack, Tree ,Node
from PredictSetGeneration import GrammarAnalyzer


class Rec:
    def __init__(self, grammar_path, token_path, tree_path):
        # 数据结构初始化
        self.grammar = []
        self.TokenStack = Stack()
        # 语法分析器初始化
        analyzer = GrammarAnalyzer()
        self.predict, self.non_terminals, self.terminals = analyzer.analyze_grammar()
        self.TreePath = tree_path

        # 加载语法规则
        with open(grammar_path) as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(" ", 20)  # 保持最大分割数
                self.grammar.append({'left': parts[0], 'right': parts[2:]})

        # 加载Token
        with open(token_path) as f:
            lines = f.readlines()
            for token in reversed(lines):
                parts = token.strip().split(" ", 20)  # 保持最大分割数
                self.TokenStack.push(parts)

        # 预测表构建
        self.non_term_map, self.predict_table = self._build_predict_table()


    def _build_predict_table(self):
        #构造LL1分析表
        non_term_map = {}
        predict_table = []
        current_row = 0

        for idx, rule in enumerate(self.grammar):
            left = rule['left']

            if left not in non_term_map:
                non_term_map[left] = current_row
                predict_table.append({t: -1 for t in self.terminals})
                current_row += 1

            row = non_term_map[left]
            for symbol in self.predict[idx+1]:  # 注意self.predict的起始索引
                predict_table[row][symbol] = idx

        return non_term_map, predict_table
    def error(ll, s):

        print(f"line:{ll + 1}  {s}")

    def parse(self):
        root = self.program()
        return root
    def program(self):
        head = self.program_head()
        part = self.program_part()
        body = self.program_body()
        root = Node('ProK', judge=True)
        root.child[0] = head
        root.child[1] = part
        root.child[2] = body
        return root
    def program_head(self):
        lineinfo = self.TokenStack.pop()
        tmp = Node('Pheadk',Lineno = lineinfo[0])

        if lineinfo[2] != 'PROGRAM':
           self.error(lineinfo[0],'missing PROGRAM')
        lineinfo = self.TokenStack.pop()
        if(lineinfo[1]=='ID'):
            tmp.name.append(lineinfo[2])
        else:
            self.error(lineinfo[0],'missing program_name')
        lineinfo = self.TokenStack.pop()
        return tmp
    def declare_part():
        type_t=init_node();type_t->nodekind=TypeK;type_t->child[0]=TypeDec();

rec = Rec("data/grammar.txt", "data/testtoken.txt","data/test.txt")
rec.program()
