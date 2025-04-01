namespace Sorac.SNL.AST;

public record class ProcDeclNode(
    int LineNum,
    string Name,
    ParamDeclNode[] Params,
    TypeDeclPartNode TypeDeclPart,
    VarDeclPartNode VarDeclPart,
    ProcDeclPartNode ProcDeclPart,
    StatementListNode Body
) : Node(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
