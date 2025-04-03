import copy
import sys


def handle_index_error(exc_type, exc_value, exc_traceback):
    if exc_type is IndexError:
        print("语法树生成有误！")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_index_error


class dealError:

    def __init__(self, non_terminals, non_term_map, predict_table, grammar):
        # 初始化错误处理类，存储语法分析所需的关键信息
        self.non_terminals = non_terminals  # 非终结符集合
        self.non_term_map = non_term_map  # 非终结符到预测表索引的映射
        self.predict_table = predict_table  # LL(1)预测分析表
        self.grammar = grammar  # 文法规则
        self.reservedWords = [  # 语言保留字列表
            "PROGRAM",
            "TYPE",
            "VAR",
            "PROCEDURE",
            "IF",
            "THEN",
            "ELSE",
            "FI",
            "WHILE",
            "DO",
            "ENDWH",
            "BEGIN",
            "END",
            "READ",
            "WRITE",
            "ARRAY",
            "OF",
            "RECORD",
            "RETURN",
            "INTEGER",
            "CHAR",
        ]
        self.delimiters = [  # 语言分隔符列表
            ".",
            ":=",
            "=",
            "<",
            "+",
            "-",
            "*",
            "/",
            ",",
            "[",
            "]",
            "..",
            ";",
            "(",
            ")",
        ]

    def _get_token_type(self, token_entry):
        # 辅助方法：从token条目中提取有效类型
        token_type = token_entry[1]
        # 特殊处理标识符和字面量类型
        if token_type in {"ID", "INTC", "CHARC"}:
            return token_type
        return token_entry[2]  # 其他类型直接返回第三元素

    def __judgeRepair2(self, SignStack, TokenStack):
        # 核心预测分析验证方法：模拟分析过程判断修复是否可行
        steps = 10  # 最大验证步数防止无限循环
        while not SignStack.isEmpty() and steps > 0:
            sign = SignStack.top()
            token = self._get_token_type(TokenStack.top())

            if sign in self.non_terminals:
                # 处理非终结符：检查预测表并展开产生式
                if self.predict_table[self.non_term_map[sign]][token] == -1:
                    return False
                SignStack.pop()
                # 获取对应产生式并逆序压栈
                production = self.grammar[
                    self.predict_table[self.non_term_map[sign]][token]
                ]["right"]
                for symbol in reversed(production):
                    if symbol != "NULL":
                        SignStack.push(symbol)
            else:
                # 处理终结符：必须严格匹配
                if sign != token:
                    return False
                SignStack.pop()
                TokenStack.pop()
            steps -= 1
        return True

    def __judgeRepair(self, sign, token):
        # 快速判断当前符号与token是否匹配
        if sign in self.non_terminals:
            # 非终结符：检查预测表中是否存在有效产生式
            return self.predict_table[self.non_term_map[sign]][token] != -1
        # 终结符：直接比较类型
        return sign == token

    def run(
        self,
        SignStack,
        TokenStack,
        sign_push_history,
        prod_length_stack,
        token_back_stack,
    ):
        # 错误处理主入口：依次尝试四种修复策略
        ErrInfo = " "
        # 保存分析过程的状态信息用于可能的回溯
        self.sign_push_history = sign_push_history
        self.prod_length_stack = prod_length_stack
        self.token_back_stack = token_back_stack
        success = False
        # 按优先级尝试不同修复方法
        for repair_method in [
            self.__error1,
            self.__error3,
            self.__error2,
            self.__error4,
            self.__error5,
        ]:

            self.sign = SignStack.top()
            self.token = self._get_token_type(TokenStack.top())
            success, ErrInfo = repair_method(SignStack, TokenStack)

            if success:
                return True, ErrInfo

        # 所有修复失败后执行错误诊断
        tmptokenstack = copy.deepcopy(TokenStack)
        ErrInfo = self._diagnose_remaining_errors(tmptokenstack)
        return False, ErrInfo

    def _diagnose_remaining_errors(self, token_stack):
        tmp_stack = copy.deepcopy(token_stack)
        recent_tokens = []
        # 收集最近的5个token，按从最近到最早的顺序
        for _ in range(token_stack.size()):
            if tmp_stack.isEmpty():
                break
            token_entry = tmp_stack.pop()
            token_type = self._get_token_type(token_entry)
            recent_tokens.append(token_type)  # 最近的token在列表前端

        # 模式1：检测数组下标范围错误（结构错误，保持原逻辑）
        for i in range(len(recent_tokens) - 2):
            if (
                recent_tokens[i] == "INTC"
                and recent_tokens[i + 1] == "."
                and recent_tokens[i + 2] == "INTC"
            ):
                return '及以后的语句至少存在数组下标范围错误，应使用".."分隔符'

        # 模式2：BEGIN未闭合（数量判断）
        begin_count = recent_tokens.count("BEGIN")
        end_count = recent_tokens.count("END")
        if begin_count > end_count:
            return '及以后的语句至少存在代码块缺少"END"'

        # 模式3：IF未闭合（数量判断）
        if recent_tokens.count("IF") > recent_tokens.count("FI"):
            return '及以后的语句至少存在IF语句缺少闭合关键字"FI"'

        # 模式4：WHILE未闭合（数量判断）
        if recent_tokens.count("WHILE") > recent_tokens.count("ENDWH"):
            return '及以后的语句至少存在WHILE循环缺少闭合关键字"ENDWH"'

        # 模式5：RECORD未闭合（考虑BEGIN和RECORD的END分配）
        record_count = recent_tokens.count("RECORD")
        if record_count > 0:
            available_ends = end_count - begin_count
            if record_count > available_ends:
                return '及以后的语句至少存在RECORD声明缺少"END"'

        # 模式6：括号未闭合（数量判断）
        if recent_tokens.count("(") > recent_tokens.count(")"):
            return '及以后的语句至少存在括号未闭合，缺少")"'
        if recent_tokens.count("[") > recent_tokens.count("]"):
            return '及以后的语句至少存在数组下标未闭合，缺少"]"'

        # 模式7：赋值符误用（结构错误，保持原逻辑）
        for i in range(len(recent_tokens) - 1):
            if recent_tokens[i] == "ID" and recent_tokens[i + 1] == "=":
                return '及以后的语句至少存在赋值语句应使用":="而非"="'

        # 模式8：过程参数括号闭合（数量判断）
        if "PROCEDURE" in recent_tokens and recent_tokens.count(
            "("
        ) > recent_tokens.count(")"):
            return '及以后的语句至少存在过程参数列表缺少闭合括号")"'

        # 模式9：数组声明缺少OF（数量判断）
        if recent_tokens.count("ARRAY") > recent_tokens.count("OF"):
            return '及以后的语句至少存在数组声明缺少"OF"关键字'

        # 模式10：IF后缺少THEN（结构错误，保持原逻辑）
        for i in range(len(recent_tokens) - 1):
            if recent_tokens[i] == "IF" and recent_tokens[i + 1] > "THEN":
                return '及以后的语句至少存在IF语句缺少"THEN"分支'

        # 默认未知错误
        return "及以后的语句存在无法识别的语法错误"

    def __repair(self, num, SignStack, TokenStack):
        # 统一修复方法调度器（当前代码未直接调用）
        handlers = {
            1: self.__error1,
            2: self.__error2,
            3: self.__error3,
            4: self.__error4,
        }
        return handlers[num](SignStack, TokenStack)

    def __error1(self, SignStack, TokenStack):
        # 修复策略1：尝试插入保留字
        for word in self.reservedWords:
            test_stack = copy.deepcopy(TokenStack)
            test_stack.push(["0", "Reserved_word", word])  # 模拟插入保留字
            # 验证插入后能否继续分析
            if self.__judgeRepair2(copy.deepcopy(SignStack), test_stack):
                TokenStack.push(["0", "Reserved_word", word])
                return True, f"缺少保留字{word}"
        return False, " "

    def __error2(self, SignStack, TokenStack):
        # 修复策略2：插入缺省常量
        if self.__judgeRepair(self.sign, "INTC"):
            TokenStack.push(["0", "INTC", "error"])  # 插入伪常量
            return True, "缺少常量"
        return False, " "

    def __error3(self, SignStack, TokenStack):
        context_delimiters = {
            "RECORD_FIELD": ";",  # 记录字段后需要分号
            "ARRAY_RANGE": "..",  # 数组范围需要双点
            "PARAM_LIST": ",",  # 参数列表需要逗号
            "DEFAULT": self.delimiters,  # 默认尝试所有
        }

        tmp_stack = copy.deepcopy(TokenStack)
        recent_tokens = []
        # 收集最近的5个token，按从最近到最早的顺序
        for _ in range(5):
            if tmp_stack.isEmpty():
                break
            token_entry = tmp_stack.pop()
            token_type = self._get_token_type(token_entry)
            recent_tokens.append(token_type)  # 最近的token在列表前端
        expected_delimiter = None

        # 判断上下文类型
        if "RECORD" in recent_tokens and ";" not in recent_tokens:
            expected_delimiter = context_delimiters["RECORD_FIELD"]
        elif "ARRAY" in recent_tokens and ".." not in recent_tokens:
            expected_delimiter = context_delimiters["ARRAY_RANGE"]
        elif "PROCEDURE" in recent_tokens and "," not in recent_tokens:
            expected_delimiter = context_delimiters["PARAM_LIST"]

        # 优先插入上下文所需分隔符
        if expected_delimiter:
            test_stack = copy.deepcopy(TokenStack)
            test_stack.push(["0", "Other", expected_delimiter])  # 模拟插入分隔符
            if self.__judgeRepair2(copy.deepcopy(SignStack), test_stack):
                TokenStack.push(["0", "Other", expected_delimiter])
                return True, f"缺少符号{expected_delimiter}"

        # 修复策略3：尝试插入分隔符
        for delimiter in self.delimiters:
            test_stack = copy.deepcopy(TokenStack)
            test_stack.push(["0", "Other", delimiter])  # 模拟插入分隔符
            if self.__judgeRepair2(copy.deepcopy(SignStack), test_stack):
                TokenStack.push(["0", "Other", delimiter])
                return True, f"缺少符号{delimiter}"
        return False, " "

    def __error4(self, SignStack, TokenStack):
        # 修复策略4：回溯分析栈并尝试插入保留字
        sign_push_history = copy.deepcopy(self.sign_push_history)
        prod_length_stack = copy.deepcopy(self.prod_length_stack)
        token_back_stack = copy.deepcopy(self.token_back_stack)
        tmpsignstack = copy.deepcopy(SignStack)
        tmptokenstack = copy.deepcopy(TokenStack)

        # 最多回溯10步
        backtrack_steps = min(sign_push_history.size(), 10)
        for x in range(backtrack_steps):
            # 恢复历史状态
            pops = prod_length_stack.pop()  # 获取需要弹出的符号数量
            for _ in range(pops):
                tmpsignstack.pop()
            tmpsignstack.push(sign_push_history.pop())  # 恢复压栈历史
            token = token_back_stack.pop()  # 恢复token历史
            if token[1] != "back":
                tmptokenstack.push(token)  # 重新压入之前弹出的token
            # 尝试每个保留字
            for word in self.reservedWords:
                test_sign = copy.deepcopy(tmpsignstack)
                test_token = copy.deepcopy(tmptokenstack)
                test_token.push(["0", "Reserved_word", word])
                if self.__judgeRepair2(test_sign, test_token):
                    for _ in range(x + 1):
                        for _ in range(self.prod_length_stack.pop()):
                            SignStack.pop()
                        SignStack.push(self.sign_push_history.pop())
                        token = self.token_back_stack.pop()
                        if token[1] != "back":
                            TokenStack.push(token)
                    TokenStack.push(["0", "Reserved_word", word])
                    return True, f"缺少保留字{word}"
        return False, " "

    def __error5(self, SignStack, TokenStack):
        # 修复策略5：删除不匹配的冗余符号
        test_stack = copy.deepcopy(TokenStack)
        if test_stack.isEmpty():
            return False, " "

        # 尝试删除当前token并验证是否可行
        deleted_token = test_stack.pop()
        if self.__judgeRepair2(copy.deepcopy(SignStack), test_stack):
            # 确认删除有效后更新原始栈
            TokenStack.pop()
            return True, f"多余符号{deleted_token[2]}"
        return False, " "
