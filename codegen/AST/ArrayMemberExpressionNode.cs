namespace Sorac.SNL.AST;

public record class ArrayMemberExpressionNode(
    int LineNum,
    ExpressionNode Array,
    ExpressionNode Index
) : AssignableExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
