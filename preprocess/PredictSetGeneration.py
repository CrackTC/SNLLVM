import copy
import os


class GrammarAnalyzer:

    def __init__(self):
        self.productions = []
        self.non_terminals = set()
        self.terminals = set()
        self.first_sets = {"": set()}
        self.follow_sets = {"": set()}
        self.predict_sets = {0: set()}

    def compute_first_for_production(self, production, terminals):
        """计算单个产生式的FIRST集合"""
        left_symbol = production[0]
        has_terminator = False

        for symbol in production[2:]:  # 遍历产生式右侧
            if symbol in terminals:  # 遇到终结符
                self.first_sets[left_symbol].add(symbol)
                has_terminator = True
                break
            elif "NULL" not in self.first_sets[symbol]:  # 非终结符且不包含空
                self.first_sets[left_symbol] = self.first_sets[left_symbol].union(
                    self.first_sets[symbol]
                )
                has_terminator = True
                break
            else:  # 非终结符且包含空，继续处理下一个符号
                self.first_sets[left_symbol] = self.first_sets[left_symbol].union(
                    self.first_sets[symbol]
                ) - {"NULL"}

        # 处理右侧全可空的情况
        if not has_terminator and (
            "NULL" in self.first_sets[production[len(production) - 1]]
        ):
            self.first_sets[left_symbol].add("NULL")

    def update_follow_for_symbol(self, production, symbol_pos, terminals):
        """更新某个符号在产生式中的FOLLOW集合"""
        current_symbol = production[symbol_pos]
        next_pos = symbol_pos + 1

        # 处理后续可能为空的符号
        while (
            next_pos < len(production)
            and production[next_pos] not in terminals
            and "NULL" in self.first_sets[production[next_pos]]
        ):
            self.follow_sets[current_symbol] = self.follow_sets[current_symbol].union(
                self.first_sets[production[next_pos]]
            ) - {"NULL"}

            next_pos += 1

        # 处理结尾或遇到不可空符号的情况
        if next_pos == len(production):
            self.follow_sets[current_symbol] = self.follow_sets[current_symbol].union(
                self.follow_sets[production[0]]
            )
        elif production[next_pos] in terminals:
            self.follow_sets[current_symbol].add(production[next_pos])
        else:
            self.follow_sets[current_symbol] = self.follow_sets[current_symbol].union(
                self.first_sets[production[next_pos]]
            )

    def compute_predict(self, production, entry_id, terminals):
        """计算预测分析表条目"""
        current_pos = 2  # 产生式右侧起始位置

        # 遍历可能为空的符号
        while (
            current_pos < len(production)
            and production[current_pos] not in terminals
            and "NULL" in self.first_sets[production[current_pos]]
        ):
            self.predict_sets[entry_id] = self.predict_sets[entry_id].union(
                self.first_sets[production[current_pos]]
            ) - {"NULL"}
            current_pos += 1

        # 处理不同结束情况
        if current_pos == len(production):
            self.predict_sets[entry_id] = self.predict_sets[entry_id].union(
                self.follow_sets[production[0]]
            )
        elif production[current_pos] in terminals:
            if production[current_pos] != "NULL":
                self.predict_sets[entry_id].add(production[current_pos])
            else:
                self.predict_sets[entry_id] = self.predict_sets[entry_id].union(
                    self.follow_sets[production[0]]
                )
        else:
            self.predict_sets[entry_id] = self.predict_sets[entry_id].union(
                self.first_sets[production[current_pos]]
            )

    def initialize_collections(self):
        """初始化所有集合"""
        # 创建初始空集合
        for nt in self.productions:
            if nt[0] not in self.first_sets.keys():
                self.first_sets.update({nt[0]: set()})
                self.follow_sets.update({nt[0]: set()})
            if nt[2] in self.terminals:
                self.first_sets[nt[0]].add(nt[2])
        # print(self.first_sets)

    def compute_first_sets(self, terminals):
        """迭代计算FIRST集合直到稳定"""
        prev_state = copy.copy(self.first_sets)
        while True:
            for prod in self.productions:
                if prod[2] not in terminals:
                    self.compute_first_for_production(prod, terminals)
            if prev_state == self.first_sets:
                break
            prev_state = copy.copy(self.first_sets)

    def compute_follow_sets(self, terminals):
        """迭代计算FOLLOW集合直到稳定"""
        self.follow_sets.update({self.productions[0][0]: {"#"}})
        prev_state = copy.copy(self.follow_sets)
        while True:
            for prod in self.productions:
                for pos in range(2, len(prod)):
                    if prod[pos] in self.non_terminals:
                        self.update_follow_for_symbol(prod, pos, terminals)
            if prev_state == self.follow_sets:
                break
            prev_state = copy.copy(self.follow_sets)

    def compute_predict_sets(self, terminals):
        num = 1
        prev_state = copy.copy(self.predict_sets)
        while True:
            for prod in self.productions:
                if num not in self.predict_sets.keys():
                    self.predict_sets.update({num: set()})
                self.compute_predict(prod, num, terminals)
                num = num + 1
            if prev_state == self.predict_sets:
                break
            prev_state = copy.copy(self.predict_sets)
            num = 1

    def analyze_grammar(
        self,
        file_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "./data/grammar.txt"
        ),
    ):
        """主分析流程"""
        # 读取文法文件
        with open(file_path) as f:
            lines = f.readlines()
            for line in lines:
                production = line.strip().split()
                self.productions.append(production)
                self.non_terminals.add(production[0])
                self.terminals.update(set(production[2:]))
        self.terminals = self.terminals - self.non_terminals
        # print(self.terminals)

        # 初始化数据结构
        self.initialize_collections()
        # print(self.first_sets)
        # 计算各集合
        self.compute_first_sets(self.terminals)
        self.compute_follow_sets(self.terminals)
        self.compute_predict_sets(self.terminals)
        # print(self.first_sets)
        # print(self.follow_sets)
        # print(self.predict_sets)
        return self.predict_sets, self.non_terminals, self.terminals


"""
if __name__ == '__main__':
    analyzer = GrammarAnalyzer()
    result = analyzer.analyze_grammar()
    with open('data\predict.txt', 'w', encoding='utf-8') as file:
        for key, value in result[0].items():
            # 用单引号包裹每个元素
            quoted_values = [f"'{item}'" for item in sorted(value)]
            set_str = "{" + ", ".join(quoted_values) + "}"
            file.write(f"{key} {set_str}\n")
"""
