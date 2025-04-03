using Sorac.SNL.AST;

namespace Sorac.SNL;

public interface IProgramVisitor<TVisitResult>
{
    TVisitResult Visit(ProgramNode node);
    TVisitResult Visit(ProgramHeadNode node);
    TVisitResult Visit(TypeDeclPartNode node);
    TVisitResult Visit(TypeDeclNode node);
    TVisitResult Visit(ArrayTypeNode node);
    TVisitResult Visit(CharTypeNode node);
    TVisitResult Visit(IntegerTypeNode node);
    TVisitResult Visit(RecordTypeNode node);
    TVisitResult Visit(TypeDefTypeNode node);
    TVisitResult Visit(VarDeclPartNode node);
    TVisitResult Visit(VarDeclNode node);
    TVisitResult Visit(ProcDeclPartNode node);
    TVisitResult Visit(ProcDeclNode node);
    TVisitResult Visit(ParamDeclNode node);
    TVisitResult Visit(StatementListNode node);
    TVisitResult Visit(AssignStatementNode node);
    TVisitResult Visit(WriteStatementNode node);
    TVisitResult Visit(ReadStatementNode node);
    TVisitResult Visit(IfStatementNode node);
    TVisitResult Visit(CallStatementNode node);
    TVisitResult Visit(WhileStatementNode node);
    TVisitResult Visit(ReturnStatementNode node);
    TVisitResult Visit(ArrayMemberExpressionNode node);
    TVisitResult Visit(RecordMemberExpressionNode node);
    TVisitResult Visit(BinaryExpressionNode node);
    TVisitResult Visit(ConstantIntExpressionNode node);
    TVisitResult Visit(ConstantCharExpressionNode node);
    TVisitResult Visit(IdentifierExpressionNode node);
}
