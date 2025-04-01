namespace Sorac.SNL.AST;

public record class AssignStatementNode(
    int LineNum,
    AssignableExpressionNode Left,
    ExpressionNode Right
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
