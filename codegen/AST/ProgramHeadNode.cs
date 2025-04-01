namespace Sorac.SNL.AST;

public record class ProgramHeadNode(
    int LineNum,
    string Name
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
