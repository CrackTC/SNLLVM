using System.Diagnostics;
using System.Reflection;
using Sorac.SNL;
using Sorac.SNL.AST;
using Sorac.SNL.Utils;

// var program = new ProgramNode(
//     new ProgramHeadNode("p"),
//     new TypeDeclPartNode([]),
//     new VarDeclPartNode([
//         new VarDeclNode(IntegerTypeNode.GetInstance(), ["i", "j", "num"]),
//         new VarDeclNode(new ArrayTypeNode(1, 20, IntegerTypeNode.GetInstance()), ["a"]),
//     ]),
//     new ProcDeclPartNode([
//         new ProcDeclNode(
//             "q",
//             [ new ParamDeclNode(false, IntegerTypeNode.GetInstance(), ["num"]) ],
//             new TypeDeclPartNode([]),
//             new VarDeclPartNode([
//                 new VarDeclNode(IntegerTypeNode.GetInstance(), ["i","j","k"]),
//                 new VarDeclNode(IntegerTypeNode.GetInstance(), ["t"])
//             ]),
//             new ProcDeclPartNode([]),
//             new StatementListNode([
//                 new AssignStatementNode(
//                     new IdentifierExpressionNode("i"),
//                     new ConstantIntExpressionNode(1)
//                 ),
//                 new AssignStatementNode(
//                     new IdentifierExpressionNode("j"),
//                     new ConstantIntExpressionNode(1)
//                 ),
//                 new WhileStatementNode(
//                     new BinaryExpressionNode(
//                         Operator.Lt,
//                         new IdentifierExpressionNode("i"),
//                         new IdentifierExpressionNode("num")
//                     ),
//                     new StatementListNode([
//                         new AssignStatementNode(
//                             new IdentifierExpressionNode("j"),
//                             new BinaryExpressionNode(
//                                 Operator.Add,
//                                 new BinaryExpressionNode(
//                                     Operator.Sub,
//                                     new IdentifierExpressionNode("num"),
//                                     new IdentifierExpressionNode("i")
//                                 ),
//                                 new ConstantIntExpressionNode(1)
//                             )
//                         ),
//                         new AssignStatementNode(
//                             new IdentifierExpressionNode("k"),
//                             new ConstantIntExpressionNode(1)
//                         ),
//                         new WhileStatementNode(
//                             new BinaryExpressionNode(
//                                 Operator.Lt,
//                                 new IdentifierExpressionNode("k"),
//                                 new IdentifierExpressionNode("j")
//                             ),
//                             new StatementListNode([
//                                 new IfStatementNode(
//                                     new BinaryExpressionNode(
//                                         Operator.Lt,
//                                         new ArrayMemberExpressionNode(
//                                             new IdentifierExpressionNode("a"),
//                                             new BinaryExpressionNode(
//                                                 Operator.Add,
//                                                 new IdentifierExpressionNode("k"),
//                                                 new ConstantIntExpressionNode(1)
//                                             )
//                                         ),
//                                         new ArrayMemberExpressionNode(
//                                             new IdentifierExpressionNode("a"),
//                                             new IdentifierExpressionNode("k")
//                                         )
//                                     ),
//                                     new StatementListNode([
//                                         new AssignStatementNode(
//                                             new IdentifierExpressionNode("t"),
//                                             new ArrayMemberExpressionNode(
//                                                 new IdentifierExpressionNode("a"),
//                                                 new IdentifierExpressionNode("k")
//                                             )
//                                         ),
//                                         new AssignStatementNode(
//                                             new ArrayMemberExpressionNode(
//                                                 new IdentifierExpressionNode("a"),
//                                                 new IdentifierExpressionNode("k")
//                                             ),
//                                             new ArrayMemberExpressionNode(
//                                                 new IdentifierExpressionNode("a"),
//                                                 new BinaryExpressionNode(
//                                                     Operator.Add,
//                                                     new IdentifierExpressionNode("k"),
//                                                     new ConstantIntExpressionNode(1)
//                                                 )
//                                             )
//                                         ),
//                                         new AssignStatementNode(
//                                             new ArrayMemberExpressionNode(
//                                                 new IdentifierExpressionNode("a"),
//                                                 new BinaryExpressionNode(
//                                                     Operator.Add,
//                                                     new IdentifierExpressionNode("k"),
//                                                     new ConstantIntExpressionNode(1)
//                                                 )
//                                             ),
//                                             new IdentifierExpressionNode("t")
//                                         )
//                                     ]),
//                                     new StatementListNode([
//                                         new AssignStatementNode(
//                                             new IdentifierExpressionNode("t"),
//                                             new ConstantIntExpressionNode(0)
//                                         )
//                                     ])
//                                 ),
//                                 new AssignStatementNode(
//                                     new IdentifierExpressionNode("k"),
//                                     new BinaryExpressionNode(
//                                         Operator.Add,
//                                         new IdentifierExpressionNode("k"),
//                                         new ConstantIntExpressionNode(1)
//                                     )
//                                 )
//                             ])
//                         ),
//                         new AssignStatementNode(
//                             new IdentifierExpressionNode("i"),
//                             new BinaryExpressionNode(
//                                 Operator.Add,
//                                 new IdentifierExpressionNode("i"),
//                                 new ConstantIntExpressionNode(1)
//                             )
//                         )
//                     ])
//                 )
//             ])
//         )
//     ]),
//     new StatementListNode([
//         new ReadStatementNode(
//             new IdentifierExpressionNode("num")
//         ),
//         new AssignStatementNode(
//             new IdentifierExpressionNode("i"),
//             new ConstantIntExpressionNode(1)
//         ),
//         new WhileStatementNode(
//             new BinaryExpressionNode(
//                 Operator.Lt,
//                 new IdentifierExpressionNode("i"),
//                 new BinaryExpressionNode(
//                     Operator.Add,
//                     new IdentifierExpressionNode("num"),
//                     new ConstantIntExpressionNode(1)
//                 )
//             ),
//             new StatementListNode([
//                 new ReadStatementNode(
//                     new IdentifierExpressionNode("j")
//                 ),
//                 new AssignStatementNode(
//                     new ArrayMemberExpressionNode(
//                         new IdentifierExpressionNode("a"),
//                         new IdentifierExpressionNode("i")
//                     ),
//                     new IdentifierExpressionNode("j")
//                 ),
//                 new AssignStatementNode(
//                     new IdentifierExpressionNode("i"),
//                     new BinaryExpressionNode(
//                         Operator.Add,
//                         new IdentifierExpressionNode("i"),
//                         new ConstantIntExpressionNode(1)
//                     )
//                 )
//             ])
//         ),
//         new CallStatementNode(
//             "q",
//             [ new IdentifierExpressionNode("num") ]
//         ),
//         new AssignStatementNode(
//             new IdentifierExpressionNode("i"),
//             new ConstantIntExpressionNode(1)
//         ),
//         new WhileStatementNode(
//             new BinaryExpressionNode(
//                 Operator.Lt,
//                 new IdentifierExpressionNode("i"),
//                 new BinaryExpressionNode(
//                     Operator.Add,
//                     new IdentifierExpressionNode("num"),
//                     new ConstantIntExpressionNode(1)
//                 )
//             ),
//             new StatementListNode([
//                 new WriteStatementNode(
//                     new ArrayMemberExpressionNode(
//                         new IdentifierExpressionNode("a"),
//                         new IdentifierExpressionNode("i")
//                     )
//                 ),
//                 new AssignStatementNode(
//                     new IdentifierExpressionNode("i"),
//                     new BinaryExpressionNode(
//                         Operator.Add,
//                         new IdentifierExpressionNode("i"),
//                         new ConstantIntExpressionNode(1)
//                     )
//                 )
//             ])
//         )
//     ])
// );

var program = Parser.ParseProgram(new PeekableStreamReader(new StreamReader(args[0])));

var filenameNoExtension = Path.GetFileNameWithoutExtension(args[0]);

var target = "mips";
var visitor = new LLVMCodeGenVisitor(target);
visitor.Visit(program);
visitor.EmitToFile($"{filenameNoExtension}.ll");
Process.Start("opt", $"-S -O3 {filenameNoExtension}.ll -o {filenameNoExtension}.opt.ll").WaitForExit();
Process.Start("llc", $"-O3 {filenameNoExtension}.opt.ll -o {filenameNoExtension}.s").WaitForExit();

var lines = File.ReadAllLines($"{filenameNoExtension}.s");
using var writer = new StreamWriter($"{filenameNoExtension}.s");

using var bootstrap = typeof(LLVMCodeGenVisitor).Assembly.GetManifestResourceStream($"Sorac.SNL.Bootstrap.{target}.bootstrap.s")!;
bootstrap.CopyTo(writer.BaseStream);
writer.WriteLine();

foreach (var line in lines)
{
    if (line.TrimStart().StartsWith('.')) continue;
    writer.WriteLine(line);
}
