namespace Sorac.SNL.AST;

public record class StatementListNode(
    int LineNum,
    StatementNode[] Statements
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
