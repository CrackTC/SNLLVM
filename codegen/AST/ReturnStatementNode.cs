namespace Sorac.SNL.AST;

public record class ReturnStatementNode(int LineNum) : StatementNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
