namespace Sorac.SNL.AST;

public record class RecordTypeNode(
    int LineNum,
    VarDeclNode[] Fields
) : TypeNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
