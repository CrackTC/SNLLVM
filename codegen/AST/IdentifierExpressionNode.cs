namespace Sorac.SNL.AST;

public record class IdentifierExpressionNode(int LineNum, string Name) : AssignableExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
