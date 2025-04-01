namespace Sorac.SNL.AST;

public abstract record class StatementNode(int LineNum) : Node(LineNum);
