# 定义栈
import sys


class Stack:

    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if len(self.items) == 0:
            print("语法树生成有误")
            sys.exit()
        return self.items.pop()

    def top(self):
        if len(self.items) == 0:
            print("语法树生成有误")
            sys.exit()
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Node:

    def __init__(self, nodeKind, Lineno=0, judge=False):
        self.nodeKind = nodeKind  # Deck/SymtK/ExpK/prok----
        self.child = []  # 子节点
        self.Sibling = None  # 兄弟节点
        self.father = None  # 父节点
        self.Lineno = Lineno  # 行数
        self.kind = {"dec": " ", "stmt": " ", "exp": " "}  # 语法树节点具体类型
        self.idnum = 0  # 标识符个数
        self.name = []  # 标识符名

        # 初始化属性结构
        self.attr = [
            {"low": 0, "up": 0, "childType": " "},  # ArrayAttr
            {"paramt": " "},  # ProcAttr
            {"op": " ", "val": 0, "varkind": " ", "type": " "},  # ExpAttr
        ]
        self.judge = judge


class Tree(object):
    _VALID_OUTPUT_NODE_TYPES = {"TypeK", "VarK", "ProcK"}
    _NODE_TYPE_MAP = {"ProcK": "ProcDecK"}

    def __init__(self):
        self.root = Node("ProK", judge=True)
        self.stack = Stack()  # 语法树栈
        self.NumStack = Stack()  # 操作数栈
        self.SignStack = Stack()  # 操作符栈
        self.getExpResult = True
        self.getExpResult2 = False
        self.expflag = 0

        # 初始化根节点子结构并反向压栈
        initial_children = [Node("PheadK"), Node("TypeK"), Node("StmLK")]
        self.root.child.extend(initial_children)
        for child in reversed(initial_children):
            self.stack.push(child)

    def _build_node_line(self, node, indent_level):
        """构建节点输出行内容"""
        parts = []
        if node.nodeKind == "StmLKStmtK":
            parts = ["   " * (indent_level - 1)]
            parts.extend(f"StmLK {str(node.Lineno)}\n")
            node.nodeKind = "StmtK"
        parts.extend(["   " * indent_level])
        node_type = self._NODE_TYPE_MAP.get(node.nodeKind, node.nodeKind)
        parts.extend([node_type, " ", str(node.Lineno)])

        processing_map = {
            "DecK": self._process_dec_node,
            "StmtK": lambda n, p: p.extend([" ", n.kind["stmt"]]),
            "ExpK": self._process_exp_node,
        }
        processor = processing_map.get(node.nodeKind)
        if processor:
            processor(node, parts)

        # 处理标识符列表
        parts.extend(f" {name}" for name in node.name[: node.idnum])
        return "".join(parts)

    def _process_dec_node(self, node, parts):
        """处理声明类型节点"""
        if node.attr[1]["paramt"] != " ":
            parts.extend([" ", node.attr[1]["paramt"]])
        parts.extend([" ", node.kind["dec"]])

        if node.kind["dec"] == "ArrayK":
            attr = node.attr[0]
            parts.extend(
                [" ", str(attr["low"]), " ", str(attr["up"]), " ", attr["childType"]]
            )

    def _process_exp_node(self, node, parts):
        """处理表达式类型节点"""
        parts.extend([" ", node.kind["exp"]])
        if (varkind := node.attr[2]["varkind"]) != " ":
            parts.extend([" ", varkind])

    def getInfNode(self, TreePath, priJudge=False):
        """输出语法树信息到文件"""
        node_stack = Stack()
        indent_stack = Stack()
        node_stack.push(self.root)
        indent_stack.push(0)

        with open(TreePath, "w") as output_file:
            while not node_stack.isEmpty():
                current_node = node_stack.pop()
                current_indent = indent_stack.pop()

                # 构建节点行并确定输出条件
                node_line = self._build_node_line(current_node, current_indent)
                should_output = (
                    current_node.judge
                    or current_node.nodeKind in self._VALID_OUTPUT_NODE_TYPES
                )

                if should_output:
                    if priJudge:
                        print(node_line)
                    output_file.write(f"{node_line}\n")

                # 处理兄弟节点
                if current_node.Sibling:
                    self._process_sibling(
                        current_node, node_stack, indent_stack, current_indent
                    )

                # 处理子节点（反向入栈保证正序处理）
                for child in reversed(current_node.child):
                    node_stack.push(child)
                    indent_stack.push(current_indent + 1)

    def _process_sibling(self, node, node_stack, indent_stack, indent_level):
        """兄弟节点处理逻辑"""
        sibling = node.Sibling
        is_proc_dec_pair = (
            node.nodeKind == "ProcDecK"
            and sibling.nodeKind == "ProcDecK"
            and not sibling.judge
        )
        if not is_proc_dec_pair:
            node_stack.push(sibling)
            indent_stack.push(indent_level)
