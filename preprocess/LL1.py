from GrammarError import dealError
from GrammarProcess import predict1
from SyntaxTree import Stack, Tree
from PredictSetGeneration import GrammarAnalyzer
import sys


def handle_index_error(exc_type, exc_value, exc_traceback):
    if exc_type is IndexError:
        print("语法树生成有误！")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_index_error


class LL1:

    def __init__(self, grammar_path, token_path, tree_path):
        # 数据结构初始化
        self.TokenStack = Stack()  # 词栈
        self.SignStack = Stack()  # 符号栈
        self.grammar = []
        self.flag = True
        # 语法分析器初始化
        analyzer = GrammarAnalyzer()
        self.predict, self.non_terminals, self.terminals = analyzer.analyze_grammar()
        self.TreePath = tree_path

        # 加载语法规则
        with open(grammar_path) as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(" ", 20)  # 保持最大分割数
                self.grammar.append({"left": parts[0], "right": parts[2:]})

        # 加载Token（保持逆序压栈逻辑）
        with open(token_path) as f:
            lines = f.readlines()
            for token in reversed(lines):
                parts = token.strip().split(" ", 20)  # 保持最大分割数
                self.TokenStack.push(parts)

        self.SignStack.push("Program")

        # 预测表构建（保持原始逻辑）
        self.non_term_map, self.predict_table = self._build_predict_table()

        self.error_handler = dealError(
            self.non_terminals, self.non_term_map, self.predict_table, self.grammar
        )
        self.errors = []
        self._init_recovery_stacks()
        self.run_success = False

    def _init_recovery_stacks(self):
        # 栈初始化
        self.sign_push_history = Stack()
        self.prod_length_stack = Stack()
        self.token_back_stack = Stack()

    def _build_predict_table(self):
        # 构造LL1分析表
        non_term_map = {}
        predict_table = []
        current_row = 0

        for idx, rule in enumerate(self.grammar):
            left = rule["left"]

            if left not in non_term_map:
                non_term_map[left] = current_row
                predict_table.append({t: -1 for t in self.terminals})
                current_row += 1

            row = non_term_map[left]
            for symbol in self.predict[idx + 1]:  # 注意self.predict的起始索引
                predict_table[row][symbol] = idx

        return non_term_map, predict_table

    # token类型
    def _get_token_type(self, token_entry):

        if token_entry[1] in {"ID", "INTC", "CHARC"}:
            return token_entry[1]
        return token_entry[2]

    # 记录错误
    def _record_error(self, token_entry, message):

        line_num = int(token_entry[0])
        # 保持行号调整逻辑
        need_adjust = True
        for keyword in ["常量", ";"]:
            if keyword in message:
                need_adjust = False
                break
        if need_adjust:
            line_num += 1
        self.errors.append({"line": line_num, "message": message})

    def _handle_error(self, current_token):
        self.flag = False
        success, msg = self.error_handler.run(
            self.SignStack,
            self.TokenStack,
            self.sign_push_history,
            self.prod_length_stack,
            self.token_back_stack,
        )
        self._record_error(current_token, msg)
        return success

    def run(self):

        syntax_tree = Tree()
        current_node = syntax_tree.root

        while not self.SignStack.isEmpty() and self.TokenStack.top()[2] != "EOF":
            current_sign = self.SignStack.top()
            current_token = self.TokenStack.top()
            token_type = self._get_token_type(current_token)

            if current_sign in self.non_terminals:

                row = self.non_term_map[current_sign]
                production_id = self.predict_table[row][token_type]

                if production_id != -1:
                    current_node = self._apply_production(
                        production_id, syntax_tree, current_token, current_node
                    )
                else:
                    if not self._handle_error(current_token):
                        break
            else:

                if current_sign == token_type:
                    self._match_terminal()
                else:
                    if not self._handle_error(current_token):
                        break

        # 最终验证逻辑，判断是否有多余符号
        if self.TokenStack.top()[2] != "EOF" and not self.errors:
            self.errors.append(
                {"line": int(self.TokenStack.top()[0]), "message": "符号栈仍有残余"}
            )
        self.run_success = self.TokenStack.top()[2] == "EOF"

        # 向文件书写语法树
        syntax_tree.getInfNode(self.TreePath)
        self.syntax_tree = syntax_tree

    def _apply_production(self, prod_id, tree, token, node):

        self.sign_push_history.push(self.SignStack.pop())
        self.token_back_stack.push(["", "back", ""])

        production = self.grammar[prod_id]["right"]
        self.prod_length_stack.push(len(production))

        # 保持逆序压栈逻辑
        for symbol in reversed(production):
            if symbol != "NULL":
                self.SignStack.push(symbol)

        # 保持语法树生成参数
        return predict1(prod_id + 1, tree, token, node)  # 保持+1偏移

    def _match_terminal(self):

        self.sign_push_history.push(self.SignStack.pop())
        self.prod_length_stack.push(0)
        self.token_back_stack.push(self.TokenStack.pop())

    def showError(self, verbose=False):
        # 错误格式输出
        if verbose:
            status = "成功" if self.flag else "失败"
            print(f'语法树生成{status}，{"可" if self.flag else "不可"}继续运行')
            for err in self.errors:
                print(f"line:{err['line']} {err['message']}")
        return (-1, self.errors) if self.errors else (0, [])
