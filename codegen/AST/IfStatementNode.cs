namespace Sorac.SNL.AST;

public record class IfStatementNode(
    int LineNum,
    ExpressionNode Condition,
    StatementListNode Then,
    StatementListNode Else
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
