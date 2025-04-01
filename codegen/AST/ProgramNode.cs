namespace Sorac.SNL.AST;

public record class ProgramNode(
    int LineNum,
    ProgramHeadNode Head,
    TypeDeclPartNode TypeDeclPart,
    VarDeclPartNode VarDeclPart,
    ProcDeclPartNode ProcDeclPart,
    StatementListNode Body
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
