namespace Sorac.SNL.AST;

public record class CharTypeNode(int LineNum) : TypeNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
