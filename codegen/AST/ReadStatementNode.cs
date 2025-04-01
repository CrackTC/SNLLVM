namespace Sorac.SNL.AST;

public record class ReadStatementNode(
    int LineNum,
    AssignableExpressionNode Variable
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
