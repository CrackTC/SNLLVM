from SyntaxTree import Node
import sys


def handle_index_error(exc_type, exc_value, exc_traceback):
    if exc_type is IndexError:
        print("语法树生成有误！")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_index_error


def get_priority(op: str) -> int:
    """获取操作符优先级"""
    priority_map = {"END": 0, "<": 1, "=": 1, "+": 2, "-": 2, "*": 3, "/": 3}
    return priority_map.get(op, -1)


def judge_node_type(token: str) -> str:
    """判断节点类型"""
    operators = {"+", "-", "*", "/", "=", "<"}
    if token in operators:
        return "OpK"
    elif token.isdigit() or (len(token) == 3 and "'" in token):
        return "ConstK"
    return "IdK"


def copyNode(x, y):
    x.nodeKind = y.nodeKind
    x.child = y.child
    x.Sibling = y.Sibling
    x.Lineno = y.Lineno
    x.kind = y.kind
    x.idnum = y.idnum  # 一个节点中的标识符的个数
    x.name = y.name
    x.attr = y.attr
    x.judge = y.judge


def process1(Tree, currentToken, preNode):
    # Program ::= ProgramHead DeclarePart ProgramBody .
    return preNode


def process2(Tree, currentToken, preNode):
    # ProgramHead ::= PROGRAM ProgramName
    PheadK = Tree.stack.pop()
    PheadK.Lineno = currentToken[0]
    PheadK.judge = True
    return PheadK


def process3(Tree, currentToken, preNode):
    # ProgramName ::= ID
    preNode.name.append(str(currentToken[2]))
    preNode.idnum += 1
    return preNode


def process4(Tree, currentToken, preNode):
    return preNode


def process5(Tree, currentToken, preNode):
    return preNode


def process6(Tree, currentToken, preNode):
    return preNode


def process7(Tree, currentToken, preNode):
    TypeK = Tree.stack.pop()
    TypeK.Lineno = currentToken[0]
    TypeK.judge = True
    TypeK.child.append(Node("DecK"))
    TypeK.Sibling = Node("VarK")
    Tree.stack.push(TypeK.Sibling)
    Tree.stack.push(TypeK.child[0])
    return TypeK


def process8(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process9(Tree, currentToken, preNode):
    Tree.stack.pop()
    return preNode


def process10(Tree, currentToken, preNode):
    return preNode


def process11(Tree, currentToken, preNode):
    preNode.name.append(str(currentToken[2]))
    preNode.idnum += 1
    return preNode


def process12(Tree, currentToken, preNode):
    return preNode


def process13(Tree, currentToken, preNode):
    return preNode


def process14(Tree, currentToken, preNode):
    preNode.kind["dec"] = "IdK"
    preNode.name.append(str(currentToken[2]))
    preNode.idnum += 1
    return preNode


def process15(Tree, currentToken, preNode):
    if preNode.kind["dec"] == "ArrayK":
        preNode.attr[0]["childType"] = "IntegerK"
    else:
        preNode.kind["dec"] = "IntegerK"
    return preNode


def process16(Tree, currentToken, preNode):
    if preNode.kind["dec"] == "ArrayK":
        preNode.attr[0]["childType"] = "CharK"
    else:
        preNode.kind["dec"] = "CharK"
    return preNode


def process17(Tree, currentToken, preNode):
    return preNode


def process18(Tree, currentToken, preNode):
    return preNode


def process19(Tree, currentToken, preNode):
    preNode.kind["dec"] = "ArrayK"
    return preNode


def process20(Tree, currentToken, preNode):
    preNode.attr[0]["low"] = currentToken[2]
    return preNode


def process21(Tree, currentToken, preNode):
    preNode.attr[0]["up"] = currentToken[2]
    return preNode


def process22(Tree, currentToken, preNode):
    preNode.kind["dec"] = "RecordK"
    preNode.Lineno = currentToken[0]
    preNode.child.append(Node("DecK"))
    Tree.stack.push(preNode)
    Tree.stack.push(preNode.child[0])
    return preNode


def process23(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process24(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process25(Tree, currentToken, preNode):
    Tree.stack.pop()
    preNode = Tree.stack.pop()
    # preNode.Lineno = currentToken[0]
    preNode.judge = True
    return preNode


def process26(Tree, currentToken, preNode):
    return preNode


def process27(Tree, currentToken, preNode):
    preNode.name.append(currentToken[2])
    preNode.idnum += 1
    return preNode


def process28(Tree, currentToken, preNode):
    return preNode


def process29(Tree, currentToken, preNode):
    return preNode


def process30(Tree, currentToken, preNode):
    return preNode


def process31(Tree, currentToken, preNode):
    return preNode


def process32(Tree, currentToken, preNode):
    VarK = Tree.stack.pop()
    if VarK.nodeKind == "TypeK":
        VarK.Sibling = Node("VarK")
        VarK = VarK.Sibling
    VarK.judge = True
    VarK.Lineno = currentToken[0]
    VarK.child.append(Node("DecK"))
    VarK.Sibling = Node("ProcK")
    VarK.Sibling.judge = True
    VarK.Sibling.child.append(Node("ProcDecK"))
    VarK.Sibling.child[0].father = VarK.Sibling
    Tree.stack.push(VarK.Sibling.child[0])
    Tree.stack.push(VarK.child[0])
    return VarK


def process33(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process34(Tree, currentToken, preNode):
    Tree.stack.pop()
    return preNode


def process35(Tree, currentToken, preNode):
    return preNode


def process36(Tree, currentToken, preNode):
    preNode.name.append(currentToken[2])
    preNode.idnum += 1
    return preNode


def process37(Tree, currentToken, preNode):
    return preNode


def process38(Tree, currentToken, preNode):
    return preNode


def process39(Tree, currentToken, preNode):
    return preNode


def process40(Tree, currentToken, preNode):
    return preNode


def process41(Tree, currentToken, preNode):
    ProcDecK = Tree.stack.pop()
    if ProcDecK == "VarK":
        ProcDecK.Sibling = Node("ProcDecK")
        ProcDecK = ProcDecK.Sibling
    elif ProcDecK == "TypeK":
        ProcDecK.Sibling = Node("VarK")
        ProcDecK = ProcDecK.Sibling
        ProcDecK.Sibling = Node("ProcK")
        ProcDecK.Sibling.judge = True
        ProcDecK.Sibling.child.append(Node("ProcDecK"))
        ProcDecK.Sibling.child[0].father = ProcDecK.Sibling
        ProcDecK = ProcDecK.Sibling.child[0]

    ProcDecK.judge = True
    ProcDecK.Lineno = currentToken[0]
    if ProcDecK.father != None:
        ProcDecK.father.Lineno = currentToken[0]
    ProcDecK.child.append(Node("DecK"))
    ProcDecK.child.append(Node("TypeK"))
    ProcDecK.child.append(Node("StmLK"))
    ProcDecK.Sibling = Node("ProcDecK")
    Tree.stack.push(ProcDecK.Sibling)
    Tree.stack.push(ProcDecK.child[2])
    Tree.stack.push(ProcDecK.child[1])
    Tree.stack.push(ProcDecK.child[0])
    return ProcDecK


def process42(Tree, currentToken, preNode):
    return preNode


def process43(Tree, currentToken, preNode):
    return preNode


def process44(Tree, currentToken, preNode):
    preNode.name.append(currentToken[2])
    preNode.idnum += 1
    return preNode


def process45(Tree, currentToken, preNode):
    Tree.stack.pop()
    return preNode


def process46(Tree, currentToken, preNode):
    return preNode


def process47(Tree, currentToken, preNode):
    return preNode


def process48(Tree, currentToken, preNode):  # ???/??/?????????/
    Tree.stack.pop()
    return preNode


def process49(Tree, currentToken, preNode):
    return preNode


def process50(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.attr[1]["paramt"] = "valparamType"
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process51(Tree, currentToken, preNode):
    DecK = Tree.stack.pop()
    DecK.Lineno = currentToken[0]
    DecK.judge = True
    DecK.attr[1]["paramt"] = "varparamType"
    DecK.Sibling = Node("DecK")
    Tree.stack.push(DecK.Sibling)
    return DecK


def process52(Tree, currentToken, preNode):
    preNode.name.append(currentToken[2])
    preNode.idnum += 1
    return preNode


def process53(Tree, currentToken, preNode):
    return preNode


def process54(Tree, currentToken, preNode):
    return preNode


def process55(Tree, currentToken, preNode):
    return preNode


def process56(Tree, currentToken, preNode):
    return preNode


def process57(Tree, currentToken, preNode):
    Tree.stack.pop()
    StmLK = Tree.stack.pop()
    StmLK.Lineno = currentToken[0]
    StmLK.judge = True
    StmLK.child.append(Node("StmtK"))
    Tree.stack.push(StmLK.child[0])
    return StmLK


def process58(Tree, currentToken, preNode):
    return preNode


def process59(Tree, currentToken, preNode):
    Tree.stack.pop()
    return preNode


def process60(Tree, currentToken, preNode):
    return preNode


def process61(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.kind["stmt"] = "IfK"
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process62(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.kind["stmt"] = "WhileK"
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process63(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.kind["stmt"] = "ReadK"
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process64(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.kind["stmt"] = "WriteK"
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process65(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.kind["stmt"] = "ReturnK"
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process66(Tree, currentToken, preNode):
    StmtK = Tree.stack.pop()
    StmtK.Lineno = currentToken[0]
    StmtK.judge = True
    StmtK.child.append(Node("ExpK"))
    StmtK.child[0].name.append(currentToken[2])
    StmtK.child[0].Lineno = currentToken[0]
    StmtK.child[0].idnum += 1
    StmtK.child[0].judge = True
    StmtK.child[0].kind["exp"] = judge_node_type(currentToken[2])
    StmtK.Sibling = Node("StmtK")
    Tree.stack.push(StmtK.Sibling)
    return StmtK


def process67(Tree, currentToken, preNode):
    preNode.kind["stmt"] = "AssignK"
    return preNode


def process68(Tree, currentToken, preNode):
    preNode.kind["stmt"] = "CallK"
    preNode.name.append(preNode.child[0].name[0])
    preNode.idnum += 1
    preNode.child[0].attr[2]["varkind"] = "IdV"
    preNode.child[0].judge = False
    return preNode


def process69(Tree, currentToken, preNode):
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[1])
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    return preNode.child[0]


def process70(Tree, currentToken, preNode):
    preNode.child.append(Node("ExpK"))
    preNode.child.append(Node("StmLKStmtK"))
    preNode.child.append(Node("StmLKStmtK"))
    Tree.stack.push(preNode.child[2])
    Tree.stack.push(preNode.child[1])
    Tree.stack.push(preNode.child[0])
    return preNode


def process71(Tree, currentToken, preNode):
    preNode.child.append(Node("ExpK"))
    preNode.child.append(Node("StmLKStmtK"))
    Tree.stack.push(preNode.child[1])
    Tree.stack.push(preNode.child[0])
    return preNode


def process72(Tree, currentToken, preNode):
    return preNode


def process73(Tree, currentToken, preNode):
    preNode.name.append(currentToken[2])
    preNode.idnum += 1
    return preNode


def process74(Tree, currentToken, preNode):
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[0])
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    return preNode


def process75(Tree, currentToken, preNode):
    return preNode


def process76(Tree, currentToken, preNode):
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[1])
    return preNode


def process77(Tree, currentToken, preNode):
    Tree.stack.pop()
    return preNode


def process78(Tree, currentToken, preNode):
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    return preNode


def process79(Tree, currentToken, preNode):
    return preNode


def process80(Tree, currentToken, preNode):
    preNode.Sibling = Node("ExpK")
    Tree.stack.push(preNode.Sibling)
    return preNode


def process81(Tree, currentToken, preNode):
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    Tree.getExpResult = False
    return preNode


def process82(Tree, currentToken, preNode):  # ???//????/
    currentP = Node("ExpK")
    currentP.name.append(currentToken[2])
    currentP.Lineno = currentToken[0]
    currentP.idnum += 1
    currentP.judge = True
    currentP.kind["exp"] = judge_node_type(currentToken[2])
    while len(Tree.SignStack.items) != 0 and get_priority(
        Tree.SignStack.top().name[0]
    ) >= get_priority(currentP.name[0]):
        t = Tree.SignStack.pop()
        Rnum = Tree.NumStack.pop()
        Lnum = Tree.NumStack.pop()
        t.judge = True
        Lnum.judge = True
        Rnum.judge = True
        t.child.append(Lnum)
        t.child.append(Rnum)
        Tree.NumStack.push(t)
    Tree.SignStack.push(currentP)
    Tree.getExpResult = True
    return currentP


def process83(Tree, currentToken, preNode):
    return preNode


def process84(Tree, currentToken, preNode):
    if currentToken[2] == ")" and Tree.expflag != 0:
        while Tree.SignStack.top().name[0] != "(":
            t = Tree.SignStack.pop()
            Rnum = Tree.NumStack.pop()
            Lnum = Tree.NumStack.pop()
            t.judge = True
            Lnum.judge = True
            Rnum.judge = True
            t.child.append(Lnum)
            t.child.append(Rnum)
            Tree.NumStack.push(t)
        Tree.SignStack.pop()
        Tree.expflag -= 1
    else:
        if Tree.getExpResult or Tree.getExpResult2:
            while Tree.SignStack.top().name[0] != "END":
                t = Tree.SignStack.pop()
                Rnum = Tree.NumStack.pop()
                Lnum = Tree.NumStack.pop()
                t.judge = True
                Lnum.judge = True
                Rnum.judge = True
                t.child.append(Lnum)
                t.child.append(Rnum)
                Tree.NumStack.push(t)
            Tree.SignStack.pop()
            currentP = Tree.stack.pop()
            t1 = Tree.NumStack.pop()
            copyNode(currentP, t1)
            Tree.getExpResult2 = False
            preNode = currentP
    return preNode


def process85(Tree, currentToken, preNode):
    currentP = Node("ExpK")
    currentP.name.append(currentToken[2])
    currentP.Lineno = currentToken[0]
    currentP.idnum += 1
    currentP.judge = True
    currentP.kind["exp"] = judge_node_type(currentToken[2])
    while len(Tree.SignStack.items) != 0 and get_priority(
        Tree.SignStack.top().name[0]
    ) >= get_priority(currentP.name[0]):
        t = Tree.SignStack.pop()
        Rnum = Tree.NumStack.pop()
        Lnum = Tree.NumStack.pop()
        t.judge = True
        Lnum.judge = True
        Rnum.judge = True
        t.child.append(Lnum)
        t.child.append(Rnum)
        Tree.NumStack.push(t)
    Tree.SignStack.push(currentP)
    return currentP


def process86(Tree, currentToken, preNode):
    return preNode


def process87(Tree, currentToken, preNode):
    return preNode


def process88(Tree, currentToken, preNode):
    currentP = Node("ExpK")
    currentP.name.append(currentToken[2])
    currentP.Lineno = currentToken[0]
    currentP.idnum += 1
    currentP.judge = True
    currentP.kind["exp"] = judge_node_type(currentToken[2])
    while len(Tree.SignStack.items) != 0 and get_priority(
        Tree.SignStack.top().name[0]
    ) >= get_priority(currentP.name[0]):
        t = Tree.SignStack.pop()
        Rnum = Tree.NumStack.pop()
        Lnum = Tree.NumStack.pop()
        t.judge = True
        Lnum.judge = True
        Rnum.judge = True
        t.child.append(Lnum)
        t.child.append(Rnum)
        Tree.NumStack.push(t)
    Tree.SignStack.push(currentP)
    return currentP


def process89(Tree, currentToken, preNode):
    currentP = Node("ExpK")
    currentP.name.append("(")
    currentP.Lineno = currentToken[0]
    Tree.SignStack.push(currentP)
    Tree.expflag += 1
    return currentP


def process90(Tree, currentToken, preNode):
    currentP = Node("ExpK")
    currentP.name.append(currentToken[2])
    currentP.Lineno = currentToken[0]
    currentP.idnum += 1
    currentP.judge = True
    currentP.kind["exp"] = judge_node_type(currentToken[2])
    Tree.NumStack.push(currentP)
    return currentP


def process91(Tree, currentToken, preNode):
    currentP = Node("ExpK")
    currentP.name.append(currentToken[2])
    currentP.Lineno = currentToken[0]
    currentP.idnum += 1
    currentP.judge = True
    currentP.kind["exp"] = judge_node_type(currentToken[2])
    Tree.NumStack.push(currentP)
    return currentP


def process92(Tree, currentToken, preNode):
    return preNode


def process93(Tree, currentToken, preNode):  # ??????????
    t = Node("ExpK")
    t.name.append(currentToken[2])
    t.Lineno = currentToken[0]
    t.idnum += 1
    t.judge = True
    Tree.NumStack.push(t)
    return t


def process94(Tree, currentToken, preNode):
    preNode.kind["exp"] = "IdK"
    preNode.attr[2]["varkind"] = "IdV"
    return preNode


def process95(Tree, currentToken, preNode):
    preNode.kind["exp"] = "IdK"
    preNode.attr[2]["varkind"] = "ArrayMembV"
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[0])
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    Tree.getExpResult2 = True
    return preNode


def process96(Tree, currentToken, preNode):
    preNode.kind["exp"] = "IdK"
    preNode.attr[2]["varkind"] = "FieldMembV"
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[0])
    return preNode


def process97(Tree, currentToken, preNode):
    ExpK = Tree.stack.pop()
    ExpK.Lineno = currentToken[0]
    ExpK.judge = True
    ExpK.name.append(currentToken[2])
    ExpK.idnum += 1
    ExpK.kind["exp"] = "IdK"
    return ExpK


def process98(Tree, currentToken, preNode):
    preNode.attr[2]["varkind"] = "IdV"
    return preNode


def process99(Tree, currentToken, preNode):
    preNode.attr[2]["varkind"] = "ArrayMembV"
    preNode.child.append(Node("ExpK"))
    Tree.stack.push(preNode.child[0])
    t = Node("ExpK")
    t.name.append("END")
    Tree.SignStack.push(t)
    Tree.getExpResult2 = True
    return preNode


def process100(Tree, currentToken, preNode):
    return preNode


def process101(Tree, currentToken, preNode):
    return preNode


def process102(Tree, currentToken, preNode):
    return preNode


def process103(Tree, currentToken, preNode):
    return preNode


def process104(Tree, currentToken, preNode):
    return preNode


def process105(Tree, currentToken, preNode):
    return preNode


def predict1(num, tree, currentToken, preNode):
    if num == 1:
        t = process1(tree, currentToken, preNode)
    elif num == 2:
        t = process2(tree, currentToken, preNode)
    elif num == 3:
        t = process3(tree, currentToken, preNode)
    elif num == 4:
        t = process4(tree, currentToken, preNode)
    elif num == 5:
        t = process5(tree, currentToken, preNode)
    elif num == 6:
        t = process6(tree, currentToken, preNode)
    elif num == 7:
        t = process7(tree, currentToken, preNode)
    elif num == 8:
        t = process8(tree, currentToken, preNode)
    elif num == 9:
        t = process9(tree, currentToken, preNode)
    elif num == 10:
        t = process10(tree, currentToken, preNode)
    elif num == 11:
        t = process11(tree, currentToken, preNode)
    elif num == 12:
        t = process12(tree, currentToken, preNode)
    elif num == 13:
        t = process13(tree, currentToken, preNode)
    elif num == 14:
        t = process14(tree, currentToken, preNode)
    elif num == 15:
        t = process15(tree, currentToken, preNode)
    elif num == 16:
        t = process16(tree, currentToken, preNode)
    elif num == 17:
        t = process17(tree, currentToken, preNode)
    elif num == 18:
        t = process18(tree, currentToken, preNode)
    elif num == 19:
        t = process19(tree, currentToken, preNode)
    elif num == 20:
        t = process20(tree, currentToken, preNode)
    elif num == 21:
        t = process21(tree, currentToken, preNode)
    elif num == 22:
        t = process22(tree, currentToken, preNode)
    elif num == 23:
        t = process23(tree, currentToken, preNode)
    elif num == 24:
        t = process24(tree, currentToken, preNode)
    elif num == 25:
        t = process25(tree, currentToken, preNode)
    elif num == 26:
        t = process26(tree, currentToken, preNode)
    elif num == 27:
        t = process27(tree, currentToken, preNode)
    elif num == 28:
        t = process28(tree, currentToken, preNode)
    elif num == 29:
        t = process29(tree, currentToken, preNode)
    elif num == 30:
        t = process30(tree, currentToken, preNode)
    elif num == 31:
        t = process31(tree, currentToken, preNode)
    elif num == 32:
        t = process32(tree, currentToken, preNode)
    elif num == 33:
        t = process33(tree, currentToken, preNode)
    elif num == 34:
        t = process34(tree, currentToken, preNode)
    elif num == 35:
        t = process35(tree, currentToken, preNode)
    elif num == 36:
        t = process36(tree, currentToken, preNode)
    elif num == 37:
        t = process37(tree, currentToken, preNode)
    elif num == 38:
        t = process38(tree, currentToken, preNode)
    elif num == 39:
        t = process39(tree, currentToken, preNode)
    elif num == 40:
        t = process40(tree, currentToken, preNode)
    elif num == 41:
        t = process41(tree, currentToken, preNode)
    elif num == 42:
        t = process42(tree, currentToken, preNode)
    elif num == 43:
        t = process43(tree, currentToken, preNode)
    elif num == 44:
        t = process44(tree, currentToken, preNode)
    elif num == 45:
        t = process45(tree, currentToken, preNode)
    elif num == 46:
        t = process46(tree, currentToken, preNode)
    elif num == 47:
        t = process47(tree, currentToken, preNode)
    elif num == 48:
        t = process48(tree, currentToken, preNode)
    elif num == 49:
        t = process49(tree, currentToken, preNode)
    elif num == 50:
        t = process50(tree, currentToken, preNode)
    elif num == 51:
        t = process51(tree, currentToken, preNode)
    elif num == 52:
        t = process52(tree, currentToken, preNode)
    elif num == 53:
        t = process53(tree, currentToken, preNode)
    elif num == 54:
        t = process54(tree, currentToken, preNode)
    elif num == 55:
        t = process55(tree, currentToken, preNode)
    elif num == 56:
        t = process56(tree, currentToken, preNode)
    elif num == 57:
        t = process57(tree, currentToken, preNode)
    elif num == 58:
        t = process58(tree, currentToken, preNode)
    elif num == 59:
        t = process59(tree, currentToken, preNode)
    elif num == 60:
        t = process60(tree, currentToken, preNode)
    elif num == 61:
        t = process61(tree, currentToken, preNode)
    elif num == 62:
        t = process62(tree, currentToken, preNode)
    elif num == 63:
        t = process63(tree, currentToken, preNode)
    elif num == 64:
        t = process64(tree, currentToken, preNode)
    elif num == 65:
        t = process65(tree, currentToken, preNode)
    elif num == 66:
        t = process66(tree, currentToken, preNode)
    elif num == 67:
        t = process67(tree, currentToken, preNode)
    elif num == 68:
        t = process68(tree, currentToken, preNode)
    elif num == 69:
        t = process69(tree, currentToken, preNode)
    elif num == 70:
        t = process70(tree, currentToken, preNode)
    elif num == 71:
        t = process71(tree, currentToken, preNode)
    elif num == 72:
        t = process72(tree, currentToken, preNode)
    elif num == 73:
        t = process73(tree, currentToken, preNode)
    elif num == 74:
        t = process74(tree, currentToken, preNode)
    elif num == 75:
        t = process75(tree, currentToken, preNode)
    elif num == 76:
        t = process76(tree, currentToken, preNode)
    elif num == 77:
        t = process77(tree, currentToken, preNode)
    elif num == 78:
        t = process78(tree, currentToken, preNode)
    elif num == 79:
        t = process79(tree, currentToken, preNode)
    elif num == 80:
        t = process80(tree, currentToken, preNode)
    elif num == 81:
        t = process81(tree, currentToken, preNode)
    elif num == 82:
        t = process82(tree, currentToken, preNode)
    elif num == 83:
        t = process83(tree, currentToken, preNode)
    elif num == 84:
        t = process84(tree, currentToken, preNode)
    elif num == 85:
        t = process85(tree, currentToken, preNode)
    elif num == 86:
        t = process86(tree, currentToken, preNode)
    elif num == 87:
        t = process87(tree, currentToken, preNode)
    elif num == 88:
        t = process88(tree, currentToken, preNode)
    elif num == 89:
        t = process89(tree, currentToken, preNode)
    elif num == 90:
        t = process90(tree, currentToken, preNode)
    elif num == 91:
        t = process91(tree, currentToken, preNode)
    elif num == 92:
        t = process92(tree, currentToken, preNode)
    elif num == 93:
        t = process93(tree, currentToken, preNode)
    elif num == 94:
        t = process94(tree, currentToken, preNode)
    elif num == 95:
        t = process95(tree, currentToken, preNode)
    elif num == 96:
        t = process96(tree, currentToken, preNode)
    elif num == 97:
        t = process97(tree, currentToken, preNode)
    elif num == 98:
        t = process98(tree, currentToken, preNode)
    elif num == 99:
        t = process99(tree, currentToken, preNode)
    elif num == 100:
        t = process100(tree, currentToken, preNode)
    elif num == 101:
        t = process101(tree, currentToken, preNode)
    elif num == 102:
        t = process102(tree, currentToken, preNode)
    elif num == 103:
        t = process103(tree, currentToken, preNode)
    elif num == 104:
        t = process104(tree, currentToken, preNode)
    elif num == 105:
        t = process105(tree, currentToken, preNode)
    return t


# syntax_tree = Tree()
# process2(syntax_tree, 1)
# print(syntax_tree.root.child[1].judge)
