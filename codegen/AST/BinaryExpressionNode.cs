namespace Sorac.SNL.AST;

public enum Operator
{
    Add,
    Sub,
    Mul,
    Lt
}

public record class BinaryExpressionNode(
    int LineNum,
    Operator Operator,
    ExpressionNode Left,
    ExpressionNode Right
) : ExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
