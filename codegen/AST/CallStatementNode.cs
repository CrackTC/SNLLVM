namespace Sorac.SNL.AST;

public record class CallStatementNode(
    int LineNum,
    string Name,
    ExpressionNode[] Arguments
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
