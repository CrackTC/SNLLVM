namespace Sorac.SNL.AST;

public abstract record class Node(int LineNum)
{
    public abstract T Accept<T>(IProgramVisitor<T> visitor);
}
