namespace Sorac.SNL.AST;

public record class ProcDeclPartNode(
    int LineNum,
    ProcDeclNode[] ProcDecls
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
