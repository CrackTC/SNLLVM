namespace Sorac.SNL.AST;

public record class ArrayTypeNode(
    int LineNum,
    int Low,
    int High,
    TypeNode ElementType
) : TypeNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
