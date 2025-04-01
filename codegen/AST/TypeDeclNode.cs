namespace Sorac.SNL.AST;

public record class TypeDeclNode(
    int LineNum,
    TypeNode Type,
    string Name
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
