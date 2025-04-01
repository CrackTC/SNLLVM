namespace Sorac.SNL.AST;

public abstract record class ExpressionNode(int LineNum) : Node(LineNum);
