using System.Diagnostics.CodeAnalysis;
using Sorac.SNL.Utils;

namespace Sorac.SNL.AST;

public static class Parser
{
    private static int GetLineLevel(string line)
    {
        return (line.Length - line.TrimStart().Length) / 3; // :(
    }

    public static ProgramNode ParseProgram(PeekableStreamReader stream)
    {
        if (stream.ReadLine()?.Trim().Split(' ') is not ["ProK", var lineNum])
            throw new Exception("Invalid program node");

        var head = ParseProgramHead(stream);
        var typeDeclPart = ParseTypeDeclPart(stream);
        var varDeclPart = ParseVarDeclPart(stream);
        var procDeclPart = ParseProcDeclPart(stream);
        var body = ParseStatementList(stream);

        return new(int.Parse(lineNum), head, typeDeclPart, varDeclPart, procDeclPart, body);
    }

    private static ProgramHeadNode ParseProgramHead(PeekableStreamReader stream)
    {
        if (stream.ReadLine()?.Trim().Split(' ') is not ["PheadK", var lineNum, var name])
            throw new Exception("Invalid program head node");

        return new ProgramHeadNode(int.Parse(lineNum), name);
    }

    private static TypeDeclPartNode ParseTypeDeclPart(PeekableStreamReader stream)
    {
        if (stream.ReadLine()?.Trim().Split(' ') is not ["TypeK", var lineNum])
            throw new Exception("Invalid type decl part node");

        var typeDeclList = new List<TypeDeclNode>();
        while (ParseTypeDecl(stream, out var typeDecl))
            typeDeclList.Add(typeDecl);

        return new TypeDeclPartNode(int.Parse(lineNum), [.. typeDeclList]);
    }

    private static bool ParseTypeDecl(PeekableStreamReader stream, [NotNullWhen(true)] out TypeDeclNode? typeDecl)
    {
        var line = stream.PeekLine()!;
        var lineLevel = GetLineLevel(line);

        if (line.Trim().Split(' ') is not ["DecK", var lineNumStr, var typeKind, .. var extra, var name])
        {
            typeDecl = default;
            return false;
        }

        stream.ReadLine();

        var lineNum = int.Parse(lineNumStr);

        switch (typeKind)
        {
            case "RecordK":
                var recordNode = ParseRecordType(stream, lineNum, lineLevel + 1);
                typeDecl = new TypeDeclNode(lineNum, recordNode, name);
                return true;
            case "ArrayK":
                var type = new ArrayTypeNode(lineNum, int.Parse(extra[0]), int.Parse(extra[1]), extra[2] switch
                {
                    "IntegerK" => new IntegerTypeNode(lineNum),
                    "CharK" => new CharTypeNode(lineNum),
                    _ => throw new NotImplementedException()
                });
                typeDecl = new TypeDeclNode(lineNum, type, name);
                return true;
            default: throw new NotImplementedException();
        }
    }

    private static RecordTypeNode ParseRecordType(PeekableStreamReader stream, int lineNum, int lineLevel)
    {
        var fieldDeclList = new List<VarDeclNode>();

        while (ParseVarDecl(stream, lineLevel, out var fieldDecl))
            fieldDeclList.Add(fieldDecl);

        return new RecordTypeNode(lineNum, [.. fieldDeclList]);
    }

    private static bool ParseVarDecl(PeekableStreamReader stream, int lineLevel, [NotNullWhen(true)] out VarDeclNode? varDecl)
    {
        var line = stream.PeekLine();
        if (line?.Trim().Split(' ') is not ["DecK", var lineNumStr, .. var remaining] || GetLineLevel(line) != lineLevel)
        {
            varDecl = default;
            return false;
        }

        stream.ReadLine();

        var lineNum = int.Parse(lineNumStr);

        switch (remaining)
        {
            case ["ArrayK", var lowStr, var highStr, var typeKind, .. var names]:
                varDecl = new VarDeclNode(lineNum, new ArrayTypeNode(lineNum, int.Parse(lowStr), int.Parse(highStr), typeKind switch
                {
                    "IntegerK" => new IntegerTypeNode(lineNum),
                    "CharK" => new CharTypeNode(lineNum),
                    _ => throw new NotImplementedException()
                }), names);
                return true;
            case ["RecordK", .. var names]:
                varDecl = new VarDeclNode(lineNum, ParseRecordType(stream, lineNum, lineLevel + 1), names);
                return true;
            case ["IntegerK", .. var names]:
                varDecl = new VarDeclNode(lineNum, new IntegerTypeNode(lineNum), names);
                return true;
            case ["CharK", .. var names]:
                varDecl = new VarDeclNode(lineNum, new CharTypeNode(lineNum), names);
                return true;
            case ["IdK", var id, .. var names]:
                varDecl = new VarDeclNode(lineNum, new TypeDefTypeNode(lineNum, id), names);
                return true;
            default:
                throw new NotImplementedException();
        }
    }

    private static VarDeclPartNode ParseVarDeclPart(PeekableStreamReader stream)
    {
        var line = stream.PeekLine();

        if (line?.Trim().Split(' ') is not ["VarK", var lineNumStr])
            return new VarDeclPartNode(0, []);

        stream.ReadLine();

        var level = GetLineLevel(line);
        var varDeclList = new List<VarDeclNode>();
        while (ParseVarDecl(stream, level + 1, out var varDecl))
            varDeclList.Add(varDecl);

        return new VarDeclPartNode(int.Parse(lineNumStr), [.. varDeclList]);
    }

    private static ProcDeclPartNode ParseProcDeclPart(PeekableStreamReader stream)
    {
        if (stream.PeekLine()?.Trim().Split(' ') is not ["ProcDecK", var lineNumStr])
            return new ProcDeclPartNode(0, []);

        stream.ReadLine();

        var procDeclList = new List<ProcDeclNode>();
        while (ParseProcDecl(stream, out var procDecl))
            procDeclList.Add(procDecl);

        return new ProcDeclPartNode(int.Parse(lineNumStr), [.. procDeclList]);
    }

    private static bool ParseProcDecl(PeekableStreamReader stream, [NotNullWhen(true)] out ProcDeclNode? procDecl)
    {
        if (stream.PeekLine()?.Trim().Split(' ') is not ["ProcDecK", var lineNumStr, var name])
        {
            procDecl = default;
            return false;
        }

        stream.ReadLine();

        var paramList = new List<ParamDeclNode>();
        while (ParseParamDecl(stream, out var paramDecl))
            paramList.Add(paramDecl);

        var typeDeclPart = ParseTypeDeclPart(stream);
        var varDeclPart = ParseVarDeclPart(stream);
        var procDeclPart = ParseProcDeclPart(stream);
        var body = ParseStatementList(stream);

        procDecl = new ProcDeclNode(int.Parse(lineNumStr), name, [.. paramList], typeDeclPart, varDeclPart, procDeclPart, body);
        return true;
    }

    private static bool ParseParamDecl(PeekableStreamReader stream, [NotNullWhen(true)] out ParamDeclNode? paramDecl)
    {
        if (stream.PeekLine()?.Trim().Split(' ') is not ["DecK", var lineNumStr, var kind, .. var remaining])
        {
            paramDecl = default;
            return false;
        }

        var level = GetLineLevel(stream.ReadLine()!);

        var lineNum = int.Parse(lineNumStr);
        var isRef = kind is not "valparamType";

        switch (remaining)
        {
            case ["IntegerK", .. var names]:
                paramDecl = new ParamDeclNode(lineNum, isRef, new IntegerTypeNode(lineNum), names);
                return true;
            case ["CharK", .. var names]:
                paramDecl = new ParamDeclNode(lineNum, isRef, new CharTypeNode(lineNum), names);
                return true;
            case ["ArrayK", var lowStr, var highStr, var typeKind, .. var names]:
                paramDecl = new ParamDeclNode(lineNum, isRef, new ArrayTypeNode(lineNum, int.Parse(lowStr), int.Parse(highStr), typeKind switch
                {
                    "IntegerK" => new IntegerTypeNode(lineNum),
                    "CharK" => new CharTypeNode(lineNum),
                    _ => throw new NotImplementedException()
                }), names);
                return true;
            case ["RecordK", .. var names]:
                paramDecl = new ParamDeclNode(lineNum, isRef, ParseRecordType(stream, lineNum, level + 1), names);
                return true;
            case ["IdK", var id, .. var names]:
                paramDecl = new ParamDeclNode(lineNum, isRef, new TypeDefTypeNode(lineNum, id), names);
                return true;
            default:
                throw new NotImplementedException();
        }
    }

    private static StatementListNode ParseStatementList(PeekableStreamReader stream)
    {
        var line = stream.ReadLine();

        if (line?.Trim().Split(' ') is not ["StmLK", var lineNumStr])
            throw new Exception("Invalid statement list node");

        var statementList = new List<StatementNode>();
        var lineLevel = GetLineLevel(line);
        while (ParseStatement(stream, lineLevel + 1, out var statement))
            statementList.Add(statement);

        return new StatementListNode(int.Parse(lineNumStr), [.. statementList]);
    }

    private static bool ParseStatement(PeekableStreamReader stream, int lineLevel, [NotNullWhen(true)] out StatementNode? statement)
    {
        var line = stream.PeekLine();

        if (line?.Trim().Split(' ') is not ["StmtK", var lineNumStr, var kind, .. var remaining] || GetLineLevel(line) is var level && level != lineLevel)
        {
            statement = default;
            return false;
        }

        var lineNum = int.Parse(lineNumStr);
        stream.ReadLine();

        switch (kind)
        {
            case "AssignK":
                if (ParseExpression(stream, level + 1, out var left) is false || left is not AssignableExpressionNode l)
                    throw new Exception("Left side of assignment is not assignable");
                if (ParseExpression(stream, level + 1, out var right) is false)
                    throw new Exception("Right side of assignment is not an expression");

                statement = new AssignStatementNode(lineNum, l, right);
                return true;
            case "CallK":
                var name = remaining[0];
                var args = new List<ExpressionNode>();
                while (ParseExpression(stream, level + 1, out var arg))
                    args.Add(arg);
                statement = new CallStatementNode(lineNum, name, [.. args]);
                return true;
            case "IfK":
                if (ParseExpression(stream, level + 1, out var condition) is false)
                    throw new Exception("Invalid if condition");
                var thenPart = ParseStatementList(stream);
                var elsePart = ParseStatementList(stream);
                statement = new IfStatementNode(lineNum, condition, thenPart, elsePart);
                return true;
            case "ReadK":
                var id = new IdentifierExpressionNode(lineNum, remaining[0]);
                statement = new ReadStatementNode(lineNum, id);
                return true;
            case "WhileK":
                if (ParseExpression(stream, level + 1, out var whileCondition) is false)
                    throw new Exception("Invalid while condition");
                var whileBody = ParseStatementList(stream);
                statement = new WhileStatementNode(lineNum, whileCondition, whileBody);
                return true;
            case "WriteK":
                if (ParseExpression(stream, level + 1, out var writeExpression) is false)
                    throw new Exception("Invalid write expression");
                statement = new WriteStatementNode(lineNum, writeExpression);
                return true;
            case "ReturnK":
                statement = new ReturnStatementNode(lineNum);
                return true;
            default:
                throw new NotImplementedException();
        }
    }

    private static bool ParseExpression(PeekableStreamReader stream, int lineLevel, [NotNullWhen(true)] out ExpressionNode? expression)
    {
        var line = stream.PeekLine();
        if (line?.Trim().Split(' ') is not ["ExpK", var lineNumStr, var kind, .. var remaining] || GetLineLevel(line) != lineLevel)
        {
            expression = default;
            return false;
        }

        stream.ReadLine();

        var lineNum = int.Parse(lineNumStr);

        switch (kind)
        {
            case "OpK":
                var op = remaining[0];
                if (ParseExpression(stream, lineLevel + 1, out var left) is false || ParseExpression(stream, lineLevel + 1, out var right) is false)
                    throw new Exception("Invalid binary expression");
                expression = new BinaryExpressionNode(lineNum, op switch
                {
                    "+" => Operator.Add,
                    "-" => Operator.Sub,
                    "*" => Operator.Mul,
                    "<" => Operator.Lt,
                    _ => throw new NotImplementedException()
                }, left, right);
                return true;
            case "ConstK":
                var value = remaining[0];
                if (value is ['\'', var c, '\''])
                    expression = new ConstantCharExpressionNode(lineNum, c);
                else expression = new ConstantIntExpressionNode(lineNum, int.Parse(value));
                return true;
            case "IdK":
                switch (remaining[0])
                {
                    case "IdV":
                        expression = new IdentifierExpressionNode(lineNum, remaining[1]);
                        return true;
                    case "ArrayMembV":
                        var arrayName = remaining[1];
                        if (ParseExpression(stream, lineLevel + 1, out var index) is false)
                            throw new Exception("Invalid array member expression");
                        expression = new ArrayMemberExpressionNode(lineNum, new IdentifierExpressionNode(lineNum, arrayName), index);
                        return true;
                    case "FieldMembV":
                        var recordName = remaining[1];
                        ParseExpression(stream, lineLevel + 1, out var field);
                        switch (field)
                        {
                            case IdentifierExpressionNode f:
                                expression = new RecordMemberExpressionNode(lineNum, new IdentifierExpressionNode(lineNum, recordName), f);
                                return true;
                            case ArrayMemberExpressionNode a:
                                if (a.Array is not IdentifierExpressionNode arrId)
                                    throw new Exception("Invalid record member expression");
                                expression = new ArrayMemberExpressionNode(
                                    a.LineNum,
                                    new RecordMemberExpressionNode(lineNum, new IdentifierExpressionNode(lineNum, recordName), arrId),
                                    a.Index
                                );
                                return true;
                            default:
                                throw new NotImplementedException();
                        }
                    default:
                        throw new NotImplementedException();
                }
            default:
                throw new NotImplementedException();
        }
    }
}
