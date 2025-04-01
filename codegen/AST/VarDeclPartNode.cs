namespace Sorac.SNL.AST;

public record class VarDeclPartNode(
    int LineNum,
    VarDeclNode[] VarDecls
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
