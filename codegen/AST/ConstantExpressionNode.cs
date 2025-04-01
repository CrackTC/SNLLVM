namespace Sorac.SNL.AST;

public record class ConstantIntExpressionNode(int LineNum, int Value) : ExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}

public record class ConstantCharExpressionNode(int LineNum, char Value) : ExpressionNode(LineNum)
{
    public override T Accept<T>(IProgramVisitor<T> visitor) => visitor.Visit(this);
}
