namespace Sorac.SNL.AST;

public record class RecordMemberExpressionNode(
    int LineNum,
    IdentifierExpressionNode Record,
    IdentifierExpressionNode Member
) : AssignableExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
