import copy
import json
import re
import sys
import os
from typing import List, Dict, Any

# 提高递归深度限制
sys.setrecursionlimit(3000)


def handle_index_error(exc_type, exc_value, exc_traceback):
    if exc_type is IndexError:
        print("语义分析有误！")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_index_error
# 全局标志，用于标记是否发生错误
flag = False


class Node:

    def __init__(self, line, val, depth):
        """
        初始化节点对象
        :param line: 行号
        :param val: 节点值
        :param depth: 节点深度
        """
        self.child = []
        self.val = val
        self.depth = depth
        self.line = str(line + 1)
        self._init_base_attributes()
        self._parse_value(val)

    def _init_base_attributes(self) -> None:
        """初始化所有节点的基本属性"""
        self.nodeKind = ""
        self.kind = ""
        self.idnum: int = 0
        self.name = []
        self.attr = {}
        self.rawline: str = ""
        self.realKind: str = ""

    def _parse_value(self, val: str) -> None:
        """主解析方法"""
        parts = val.split()
        self.nodeKind = parts[0]
        self.rawline = str(int(parts[1]) + 1)
        remaining = parts[2:]

        # 使用分派模式处理不同节点类型
        parser = {
            "DecK": self._parse_dec,
            "StmtK": self._parse_stmt,
            "ExpK": self._parse_exp,
        }.get(self.nodeKind, self._parse_default)

        remaining = parser(remaining)
        self._process_remaining_identifiers(remaining)

    def _parse_dec(self, vals: List[str]) -> List[str]:
        """处理声明类型节点"""
        # 处理参数类型前缀
        if vals and vals[0] in ("valparamType", "varparamType"):
            self.attr["paramt"] = vals[0]
            vals = vals[1:]

        self.kind = vals[0]
        vals = vals[1:]

        # 处理特殊类型
        if self.kind == "IdK":
            self.realKind = vals[0]
            vals = vals[1:]

        # 处理数组类型
        if self.kind == "ArrayK":
            self.attr.update({"low": vals[0], "up": vals[1], "childType": vals[2]})
            vals = vals[3:]
        return vals

    def _parse_stmt(self, vals: List[str]) -> List[str]:
        """处理语句类型节点"""
        if vals:
            self.kind = vals[0]
            return vals[1:]
        return vals

    def _parse_exp(self, vals: List[str]) -> List[str]:
        """处理表达式类型节点"""
        if vals:
            self.kind = vals[0]
            vals = vals[1:]

        # 处理变量类型
        if vals and vals[0] in ("IdV", "ArrayMembV", "FieldMembV"):
            self.attr["varkind"] = vals[0]
            vals = vals[1:]

        # 处理操作符和常量
        if self.kind == "OpK" and vals:
            self.attr["op"] = vals[0]
        elif self.kind == "ConstK" and vals:
            self.attr["val"] = vals[0]
        return vals

    def _parse_default(self, vals: List[str]) -> List[str]:
        """默认解析处理"""
        return vals

    def _process_remaining_identifiers(self, vals: List[str]) -> None:
        """处理剩余标识符"""
        self.name = [x for x in vals if x]
        self.idnum = len(self.name)

    def __str__(self) -> str:
        """简化字符串表示"""
        return str(self.__dict__)

    def print(self) -> None:
        """结构化打印方法"""
        print(str(json.dumps(self.__dict__)))


class DefaultKind:

    def __init__(self, kind):
        """
        初始化默认类型对象
        :param kind: 类型名称
        """
        self.kind = kind


class Kind:

    def __init__(self, node, body=None):
        """
        初始化类型对象
        :param node: 节点对象
        :param body: 子节点列表
        """
        self.kind = node.kind
        self.size = 0
        if node.kind == "ArrayK":
            indexTy = {"low": node.attr["low"], "up": node.attr["up"]}
            elemTy = Kind(DefaultKind(node.attr["childType"])).__dict__
            self.arrayAttr = {"indexTy": indexTy, "elemTy": elemTy}
            self.size = elemTy["size"] * (int(node.attr["up"]) - int(node.attr["low"]))
            self.arrayKind = elemTy["kind"]
        if node.kind == "RecordK":
            if body:
                for x in body:
                    self.size += x.size
        if node.kind == "IntegerK":
            self.size = 2
        if node.kind == "CharK":
            self.size = 1

    def __str__(self):
        """字符串表示"""
        return str(self.__dict__)


class SymbolTable:

    def __init__(self, node, name, level, off, body=None, params=None, is_type=False):
        """
        初始化符号表对象
        :param node: 节点对象
        :param name: 符号名称
        :param level: 作用域级别
        :param off: 偏移量
        :param body: 子节点列表
        :param params: 参数列表
        :param is_type: 是否为类型
        """

        self.kind = node.kind
        self.name = name
        self.level = level
        self.off = off
        self.params = params
        self.is_type = is_type
        self.body = self._process_body(body, node, name)
        self.typePtr = Kind(node, self.body)

    def _process_body(self, body, node, name):
        """处理 body 数据，检查字段名重复并生成符号条目"""
        if body is None:
            return None

        entries = []
        seen_names = set()

        for line_num, field_node in enumerate(body, start=1):
            for field_name in field_node.name:
                if field_name in seen_names:
                    error_line = int(node.rawline) + line_num
                    error(
                        str(error_line),
                        f"record {name} field member {field_name} duplicated",
                    )
                    continue

                seen_names.add(field_name)
                entries.append(self._create_entry(field_node, field_name))

        return entries

    def _create_entry(self, field_node, field_name):
        """创建类型条目并设置字段名"""
        entry = Kind(field_node)
        entry.name = field_name
        return entry

    def __str__(self):
        """结构化显示符号表信息"""
        body_str = (
            "".join(str(entry.__dict__) for entry in self.body) if self.body else ""
        )

        return (
            f"SymbolTable(kind={self.kind}, name={self.name}, "
            f"level={self.level}, off={self.off}, typePtr={self.typePtr.__dict__}, "
            f"body=[{body_str}], params={self.params}, is_type={self.is_type})"
        )


# 全局作用域和当前作用域
all_scope = [[]]
scope = [[]]
sl = 0
off = 0


def error(*params: Any) -> None:
    """
    打印错误信息并标记错误标志
    :param params: 错误信息参数
    """
    global flag
    flag = True
    message = []
    for param in params:
        if isinstance(param, str):
            message.append(param)
        else:
            message.append(str(param))
    print(f"line: {' '.join(message)}")


def dfs(node):
    """
    深度优先遍历节点
    :param node: 节点对象
    """
    for child in node.child:
        print(f"{node.val} -> {child.val}")
    for child in node.child:
        dfs(child)


def generate_node(tree_path):
    """
    从文件中生成节点树
    :param tree_path: 文件路径
    :return: 根节点
    """
    hierarchy = {}
    with open(tree_path) as file:
        for line_num, line in enumerate(file):
            line_content = line.rstrip("\n").lstrip(" ")
            indent_level = (len(line) - len(line_content)) // 3

            if line_content == "StmLK":
                continue

            current_node = Node(line_num, line_content, indent_level)
            hierarchy.setdefault(indent_level, []).append(current_node)

            if indent_level > 0:
                parent_level = indent_level - 1
                if parent_level in hierarchy:
                    parent = hierarchy[parent_level][-1]
                    parent.child.append(current_node)

    return hierarchy[0][0] if hierarchy else None


def CallSymbolTable(node, name, level, off, body=None, params=None, is_type=False):
    """
    创建符号表条目
    :param node: 节点对象
    :param name: 符号名称
    :param level: 作用域级别
    :param off: 偏移量
    :param body: 子节点列表
    :param params: 参数列表
    :param is_type: 是否为类型
    :return: 符号表条目
    """
    # 处理非标识符节点的情况
    if node.kind != "IdK":
        return SymbolTable(
            node=node,
            name=name,
            level=level,
            off=off,
            body=body,
            params=params,
            is_type=is_type,
        )

    # 处理标识符节点的类型查找逻辑
    type_entry = find(node.realKind, type_flag=True)
    if type_entry is None:
        error(node.rawline, f"unknown kind: {node.realKind}")
        return None

    # 克隆类型条目并设置属性
    symbol_table = copy.deepcopy(type_entry)
    symbol_table.is_type = False
    symbol_table.name = name
    return symbol_table


def find(name, exist=None, type_flag=False):
    """
    在作用域中查找指定名称和类型的符号
    :param name: 符号名称
    :param exist: 是否存在标志
    :param type_flag: 是否为类型标志
    :return: 符号表条目
    """
    low = sl - 1 if exist is not None else -1
    for i in range(sl, low, -1):
        for entry in reversed(scope[i]):
            if entry.name == name and entry.is_type == type_flag:
                return entry
    return None


# 使用字典存储类型验证规则，提升可维护性
KIND_VALIDATION = {
    "IdV": ("IntegerK", "CharK"),
    "ArrayMembV": ("ArrayK",),
    "FieldMembV": ("RecordK",),
}


def validate_kind(kind, vkind):
    """
    验证变量类型是否符合规范
    :param kind: 变量类型
    :param vkind: 验证类型
    :return: 是否符合规范
    """
    return vkind in KIND_VALIDATION.get(kind, ())


def get_field_kind(field):
    """
    获取字段类型
    :param field: 字段对象
    :return: 字段类型
    """
    if field.kind in ("IntegerK", "CharK"):
        return field.kind
    if field.kind == "ArrayK":
        return field.arrayKind
    return None


def create_name(node):
    """
    生成复合名称
    :param node: 节点对象
    :return: 复合名称
    """
    if node.attr.get("varkind") == "FieldMembV":
        return f"{node.name[0]}.{node.child[0].name[0]}"
    return node.name[0]


def getKind(node):
    """
    获取节点类型的主逻辑
    :param node: 节点对象
    :return: 节点类型
    """
    if node.kind == "ConstK":
        return _handle_const(node)
    if node.kind == "IdK":
        return _handle_identifier(node)
    if node.kind == "OpK":
        return operator(node, node.name[0])
    return None


def _handle_const(node):
    """
    处理常量类型
    :param node: 节点对象
    :return: 常量类型
    """
    name = node.name[0]
    if name.isdigit():
        return "IntegerK"
    if re.match(r"^'[a-zA-Z]'$", name):
        return "CharK"
    return None


def _handle_identifier(node):
    """
    处理标识符类型
    :param node: 节点对象
    :return: 标识符类型
    """
    kind = node.attr["varkind"]
    symbol = find(node.name[0])

    if not symbol:
        error(node.rawline, "未找到符号:", node.name[0])
        return None

    # if not validate_kind(kind, symbol.kind):
    #     error(node.rawline, "类型不匹配:", node.name[0], kind, symbol.kind)
    #     return None

    if kind == "IdV":
        return symbol.kind

    if kind == "ArrayMembV":
        return _handle_array(node, symbol)

    if kind == "FieldMembV":
        return _handle_record(node, symbol)


def _handle_array(node, symbol):
    """
    处理数组类型
    :param node: 节点对象
    :param symbol: 符号表条目
    :return: 数组元素类型
    """
    if len(node.child) != 1:
        error(node.rawline, "数组操作错误:", node.name[0])
        return None

    index_node = node.child[0]
    index_type = getKind(index_node)

    # 验证索引类型
    if not index_type or index_type != "IntegerK":
        error(index_node.rawline, "非法数组索引:", create_name(index_node))
        return None

    # 验证索引范围
    index_attr = symbol.typePtr.arrayAttr["indexTy"]
    low, up = int(index_attr["low"]), int(index_attr["up"])
    if index_node.name[0].isdigit() and not (low <= int(index_node.name[0]) <= up):
        error(node.rawline, "数组索引越界:", f"{index_node.name[0]} (范围: {low}-{up})")

    return symbol.typePtr.arrayKind


def _handle_record(node, symbol):
    """
    处理记录类型
    :param node: 节点对象
    :param symbol: 符号表条目
    :return: 记录成员类型
    """
    member_name = node.child[0].name[0]
    member = next((x for x in symbol.body if x.name == member_name), None)

    if not member:
        error(node.rawline, f"记录 {node.name[0]} 缺少成员 {member_name}")
        return None

    if not validate_kind(node.child[0].attr["varkind"], member.kind):
        error(node.rawline, "成员类型不匹配:", member_name, member.kind)
        return None

    # 生成子节点符号表
    for child in node.child[0].child:
        generate_table(child)

    return get_field_kind(member)


def operator(node, op):
    """
    处理操作符类型检查
    :param node: 节点对象
    :param op: 操作符
    :return: 操作结果类型
    """
    global sl, scope, off

    operand_kinds = [generate_table(x) for x in node.child]
    if None in operand_kinds:
        return None

    # 统一操作数类型检查
    base_type = operand_kinds[0]
    if not all(k == base_type for k in operand_kinds):
        error_details = [(n.name[0], k) for n, k in zip(node.child, operand_kinds)]
        error(node.rawline, f"操作数类型不一致 {op}:", error_details)
        return None

    # 运算符特殊规则检查
    if op in ("+", "-", "*", "/") and base_type == "CharK":
        error(node.rawline, f"运算符 {op} 不能用于字符类型")
        return None

    return base_type


def generate_table(node):
    """
    生成符号表
    :param node: 节点对象
    :return: 节点类型
    """
    global sl, scope, off
    node_handlers = {
        "DecK": handle_declaration,
        "ProcDecK": handle_procedure,
        "StmtK": handle_statement,
        "ExpK": handle_expression,
        "TypeK": handle_type,
    }
    handler = node_handlers.get(node.nodeKind, handle_default)
    return handler(node)


def handle_record(node):
    """
    处理记录类型声明
    :param node: 节点对象
    """
    global sl, scope, off
    for name in node.name:
        if check_duplicate(name, node.rawline, "record"):
            continue

        body = []
        for y in node.child:
            body.append(y)
        # 创建符号表条目并传递子节点作为body
        entry = CallSymbolTable(
            node=node,
            name=name,
            level=sl,
            off=off,
            body=body,  # 直接传递node的子节点作为body
        )
        if not entry:
            continue

        update_scope(entry)


def handle_declaration(node):
    """
    处理声明节点
    :param node: 节点对象
    """
    global sl, scope, off
    if node.kind == "RecordK":
        handle_record(node)
        return

    for name in node.name:
        if check_duplicate(name, node.rawline, "val"):
            continue

        entry = CallSymbolTable(node=node, name=name, level=sl, off=off, body=None)
        if not entry:
            continue

        update_scope(entry)

        for child in node.child:
            generate_table(child)


def handle_procedure(node):
    """
    处理过程声明节点
    :param node: 节点对象
    """
    global sl, scope, off
    if node.idnum <= 0:
        handle_default(node)
        return

    if check_duplicate(node.name[0], node.rawline, "proc"):
        return

    # 收集形式参数
    params = []
    for child in node.child:
        if child.nodeKind == "DecK":
            if child.kind == "ArrayK":
                for name in child.name:
                    if name != " " and name != "":
                        params.append(
                            {
                                "kind": child.kind
                                + " "
                                + child.attr["low"]
                                + " "
                                + child.attr["up"]
                                + " "
                                + child.attr["childType"],
                                "name": name,
                            }
                        )
            else:
                for name in child.name:
                    if name != " " and name != "":
                        if (
                            "paramt" in child.attr
                            and child.attr["paramt"] == "varparamType"
                        ):
                            if child.kind != "RecordK":
                                tmpkind = child.kind + "var"
                            else:
                                tmpkind = child.kind
                        else:
                            tmpkind = child.kind
                        if child.kind == "RecordK":
                            for ch in child.child:
                                if ch.kind == "IntegerK":
                                    tmpkind += " IntegerK" * ch.idnum
                                if ch.kind == "ArrayK":
                                    tmpkind += (
                                        " ArrayK"
                                        + ch.attr["low"]
                                        + " "
                                        + ch.attr["up"]
                                        + " "
                                        + ch.attr["childType"]
                                    )

                        params.append({"kind": tmpkind, "name": name})
    node.kind = "ProcDecK"
    # 创建符号表条目
    entry = CallSymbolTable(
        node=node, name=node.name[0], level=sl, off=off, params=params
    )
    if not entry:
        return

    update_scope(entry)

    # 进入新的作用域处理过程体
    enter_scope()
    for child in node.child:
        generate_table(child)
    exit_scope()


def handle_statement(node):
    """
    处理语句节点
    :param node: 节点对象
    """
    stmt_handlers = {
        "CallK": handle_call,
        "IfK": handle_conditional,
        "AssignK": handle_assignment,
        "ReadK": handle_read,
        "WriteK": handle_write,
        "WhileK": handle_loop,
    }
    handler = stmt_handlers.get(node.kind, lambda n: None)
    handler(node)


def handle_expression(node):
    """
    处理表达式节点
    :param node: 节点对象
    :return: 表达式类型
    """
    global sl, scope, off
    if node.kind == "OpK":
        return operator(node, node.name[0])
    return getKind(node) if node.kind in ("IdK", "ConstK") else None


def handle_type(node):
    """
    处理类型节点
    :param node: 节点对象
    """
    global sl, scope, off
    for child in node.child:
        if child.kind == "RecordK":
            generate_table(child)
            continue

        if check_duplicate(child.name[0], node.rawline, "type"):
            continue

        entry = create_symbol_entry(node=child, name=child.name[0], is_type=True)
        if entry:
            update_scope(entry)


# 辅助函数模块
def create_symbol_entry(node, name, **kwargs):
    """
    创建符号表条目
    :param node: 节点对象
    :param name: 符号名称
    :param kwargs: 其他参数
    :return: 符号表条目
    """
    return CallSymbolTable(node=node, name=name, level=sl, off=off, **kwargs)


def update_scope(entry):
    """
    更新作用域
    :param entry: 符号表条目
    """
    global sl, scope, off
    if len(scope[sl]) != 0:
        last_entry = scope[sl][-1]
        entry.off = last_entry.off + last_entry.typePtr.size
    else:
        entry.off = 0

    scope[sl].append(entry)
    all_scope[sl].append(entry)


def check_duplicate(name, line, category):
    """
    检查符号是否重复
    :param name: 符号名称
    :param line: 行号
    :param category: 符号类别
    :return: 是否重复
    """
    global sl, scope, off
    if find(name, exist=True) is not None:
        error(line, f"{category} duplicated:", name)
        return True
    return False


def enter_scope():
    """进入新的作用域"""
    global sl, scope, off
    sl += 1
    scope.append([])
    all_scope.append([])


def exit_scope():
    """退出当前作用域"""
    global sl, scope, off
    sl -= 1
    scope = scope[:-1]


# 语句处理子模块
def handle_call(node):
    """
    处理调用语句
    :param node: 节点对象
    """
    global sl, scope, off

    proc = find(node.name[0])
    if proc is None:
        error(node.rawline, "procDeck find failed:", node.name[0])
        return
    elif proc.kind != "ProcDecK":
        error(node.rawline, "procDeck kind error:", node.name[0], proc.kind)
        return

    params = []
    for param_node in node.child:
        param_type = None
        if param_node.kind == "OpK":
            param_type = operator(param_node, param_node.name[0])
            param_type += "!!"
        else:
            low = -1
            flag = False
            for i in range(sl, low, -1):
                if flag:
                    break
                for entry in reversed(scope[i]):
                    if str(entry.name) == str(param_node.name[0]):
                        flag = True
                        if (
                            entry.kind == "ArrayK"
                            and param_node.attr["varkind"] == "IdV"
                        ):
                            param_type = (
                                "ArrayK"
                                + " "
                                + entry.typePtr.arrayAttr["indexTy"]["low"]
                                + " "
                                + entry.typePtr.arrayAttr["indexTy"]["up"]
                                + " "
                                + entry.typePtr.arrayAttr["elemTy"]["kind"]
                            )
                        if (
                            entry.kind == "RecordK"
                            and param_node.attr["varkind"] == "IdV"
                        ):
                            param_node.attr["varkind"] = "FieldMembV"
                            param_type = "RecordK"
                            for body in entry.body:
                                if body.kind == "IntegerK":
                                    param_type += " IntegerK"
                                else:
                                    param_type += (
                                        " ArrayK"
                                        + body.arrayAttr["indexTy"]["low"]
                                        + " "
                                        + body.arrayAttr["indexTy"]["up"]
                                        + " "
                                        + body.arrayAttr["elemTy"]["kind"]
                                    )

                        break

            if not param_type:
                param_type = getKind(param_node)
                if param_node.kind == "ConstK":
                    param_type += "!!"
        if not param_type:
            error(param_node.rawline, "Invalid parameter type")
            return
        params.append(param_type)

    validate_parameters(proc, params, node.rawline)


def handle_conditional(node):
    """
    处理条件语句
    :param node: 节点对象
    """
    global sl, scope, off
    for child in node.child:
        generate_table(child)


def handle_assignment(node):
    """
    处理赋值语句
    :param node: 节点对象
    :return: 赋值结果类型
    """
    global sl, scope, off
    if node.child[0].kind != "IdK":
        error(node.rawline, "Invalid assignment target")
    return operator(node, "=")


def handle_read(node):
    """
    处理读取语句
    :param node: 节点对象
    """
    if not find(node.name[0]):
        error(node.rawline, "Undefined variable:", node.name[0])


def handle_write(node):
    """
    处理写入语句
    :param node: 节点对象
    :return: 写入结果类型
    """
    return operator(node, "write")


def handle_loop(node):
    """
    处理循环语句
    :param node: 节点对象
    """
    for child in node.child:
        generate_table(child)


# 验证模块
def validate_procedure(proc, node):
    """
    验证过程是否有效
    :param proc: 过程符号表条目
    :param node: 节点对象
    :return: 是否有效
    """
    if not proc:
        error(node.rawline, "Procedure not found:", node.name[0])
        return False
    if proc.kind != "ProcDecK":
        error(node.rawline, "Not a procedure:", node.name[0])
        return False
    return True


def validate_parameters(proc, params, line):
    """
    验证过程参数是否匹配
    :param proc: 过程符号表条目
    :param params: 参数列表
    :param line: 行号
    """
    expected = [p["kind"] for p in proc.params]
    if len(params) != len(expected):
        error(line, "Parameter mismatch:", params, expected)
    for i, _ in enumerate(params):
        if expected[i][-3:] == "var" and params[i][-2:] == "!!":
            error(line, "Parameter mismatch:", expected[i], params[i])
        else:
            if expected[i][-3:] == "var":
                expected[i] = expected[i][:-3]
            if params[i][-2:] == "!!":
                params[i] = params[i][:-2]
            if expected[i] != params[i]:
                error(line, "Parameter mismatch:", expected[i], params[i])


def handle_default(node):
    """
    处理默认节点
    :param node: 节点对象
    """
    for child in node.child:
        generate_table(child)


def table_print(table):
    """
    打印符号表
    :param table: 符号表
    """
    for i in range(len(table)):
        for x in table[i]:
            print(f"i:{i}, ", str(x))


root = None


def init():
    """初始化全局变量"""
    global root, all_scope, sl, off, flag, scope
    root = None
    all_scope = [[]]
    scope = [[]]
    sl = 0
    off = 0
    flag = False


def semantic(tree_path, output_path):
    """
    进行语义分析
    :param tree_path: 树文件路径
    :return: 错误标志
    """
    global root
    init()
    root = generate_node(tree_path)
    # visTree(root)  # 按需取消注释可视化
    generate_table(root)

    with open(output_path, "w") as f:
        for scope_level, scope in enumerate(all_scope):
            for symbol_entry in scope:
                f.write(f"line:{scope_level}\n")
                for key, value in symbol_entry.__dict__.items():
                    if value is None:
                        continue
                    if isinstance(value, list):
                        f.write(f"{key}:\n")
                        for item in value:
                            f.write(f"   {item}\n")
                    else:
                        f.write(f"{key}:{value}\n")
                f.write("\n")

    print("all_scope:")
    table_print(all_scope)
    return -1 if flag else 0


"""
if __name__ == '__main__':
    init()
    semantic("data/test.txt")'
"""
