namespace Sorac.SNL.AST;

public record class TypeDeclPartNode(
    int LineNum,
    TypeDeclNode[] TypeDecls
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
