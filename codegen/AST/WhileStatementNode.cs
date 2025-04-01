namespace Sorac.SNL.AST;

public record class WhileStatementNode(
    int LineNum,
    ExpressionNode Condition,
    StatementListNode Body
) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
