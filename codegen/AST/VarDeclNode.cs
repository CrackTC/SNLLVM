namespace Sorac.SNL.AST;

public record class VarDeclNode(
    int LineNum,
    TypeNode Type,
    string[] Ids
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
