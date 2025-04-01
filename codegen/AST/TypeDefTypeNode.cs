namespace Sorac.SNL.AST;

public record class TypeDefTypeNode(
    int LineNum,
    string Identifier
) : TypeNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
