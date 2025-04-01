namespace Sorac.SNL.AST;

public record class WriteStatementNode(
    int LineNum,
    ExpressionNode Expression
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
