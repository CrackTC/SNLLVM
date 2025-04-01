namespace Sorac.SNL.AST;

public record class ParamDeclNode(
    int LineNum,
    bool ByRef,
    TypeNode Type,
    string[] Ids
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
