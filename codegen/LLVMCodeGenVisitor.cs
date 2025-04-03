using LLVMSharp.Interop;
using Sorac.SNL.AST;
using Sorac.SNL.Proc;
using Sorac.SNL.Type;
using Sorac.SNL.Var;
using Sorac.SNL.Utils;

namespace Sorac.SNL;

public abstract record class LLVMCodeGenVisitorResult
{
    public record class VoidResult : LLVMCodeGenVisitorResult;
    public record class ValueResult(LLVMValueRef Value, TypeInfo TypeInfo, bool IsLValue) : LLVMCodeGenVisitorResult;
    public record class TypeResult(TypeInfo TypeInfo) : LLVMCodeGenVisitorResult;
}

public class SemanticException : Exception
{
    public SemanticException(int lineNum, string node, string message)
        : base($"Semantic error at line {lineNum} in {node}: {message}")
    {
    }
}

public unsafe class LLVMCodeGenVisitor(string targetTriple) : IProgramVisitor<LLVMCodeGenVisitorResult>
{
    private LLVMTargetMachineRef _machine;
    private LLVMModuleRef _module;
    private LLVMBuilderRef _builder;
    private LLVMPassManagerRef _passManager;

    private readonly ScopedDictionary<string, VarInfo, ProcInfo> _varTable = new(); // TExtra is ProcInfo of the scope
    private readonly ScopedDictionary<string, ProcInfo, object?> _procTable = new(); // TExtra not used
    private readonly ScopedDictionary<string, TypeInfo, object?> _typeTable = new(); // TExtra not used

    public void EmitToFile(string filename) => _module.PrintToFile(filename);

    public LLVMCodeGenVisitorResult Visit(ProgramNode node)
    {
        node.Head.Accept(this);

        var startType = LLVMTypeRef.CreateFunction(LLVMTypeRef.Void, [], IsVarArg: false);
        var startFunction = _module.AddFunction("_start", startType);

        // top-level proc, empty closure
        // not adding it to _procTable
        var emptyStruct = LLVMTypeRef.CreateStruct([], Packed: false);
        var procInfo = new ProcInfo(startFunction, startType, Level: 0, new RecordTypeInfo(emptyStruct, []), []);

        using (_typeTable.EnterScope(null))
        using (_varTable.EnterScope(procInfo))
        using (_procTable.EnterScope(null))
        {
            node.TypeDeclPart.Accept(this);

            var entryBlock = startFunction.AppendBasicBlock("entry");
            _builder.PositionAtEnd(entryBlock); // for variable allocation
            node.VarDeclPart.Accept(this);

            node.ProcDeclPart.Accept(this);

            _builder.PositionAtEnd(entryBlock); // for body code
            node.Body.Accept(this);
            _builder.BuildRetVoid();
        }

        if (!startFunction.VerifyFunction(LLVMVerifierFailureAction.LLVMPrintMessageAction))
            throw new Exception($"Error verifying function");

        _passManager.RunFunctionPassManager(startFunction);

        _module.Verify(LLVMVerifierFailureAction.LLVMPrintMessageAction);

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ProgramHeadNode node)
    {
        LLVM.InitializeMipsTargetInfo();
        LLVM.InitializeMipsTarget();
        LLVM.InitializeMipsTargetMC();
        LLVM.InitializeMipsAsmParser();
        LLVM.InitializeMipsAsmPrinter();

        _machine = LLVMTargetRef.GetTargetFromTriple(targetTriple).CreateTargetMachine(
            triple: targetTriple,
            cpu: "generic",
            features: "",
            LLVMCodeGenOptLevel.LLVMCodeGenLevelDefault,
            LLVMRelocMode.LLVMRelocStatic,
            LLVMCodeModel.LLVMCodeModelSmall
        );

        _module = LLVMModuleRef.CreateWithName($"SNL Program {node.Name}");
        _module.Target = targetTriple;
        LLVM.SetModuleDataLayout(_module, _machine.CreateTargetDataLayout());

        _builder = _module.Context.CreateBuilder();

        _passManager = _module.CreateFunctionPassManager();
        // _passManager.AddBasicAliasAnalysisPass();
        // _passManager.AddTypeBasedAliasAnalysisPass();
        // _passManager.AddPromoteMemoryToRegisterPass();
        // _passManager.AddScalarReplAggregatesPass();
        // _passManager.AddInstructionCombiningPass();
        // _passManager.AddReassociatePass();
        // _passManager.AddGVNPass();
        // _passManager.AddCFGSimplificationPass();
        // _passManager.AddAggressiveDCEPass();
        // _passManager.AddDeadStoreEliminationPass();
        if (_passManager.InitializeFunctionPassManager())
            throw new Exception($"Error initializing function pass manager");

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(TypeDeclPartNode node)
    {
        foreach (var typeDecl in node.TypeDecls)
            typeDecl.Accept(this);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(TypeDeclNode node)
    {
        if (node.Type.Accept(this) is not LLVMCodeGenVisitorResult.TypeResult { TypeInfo: var type })
            throw new SemanticException(node.LineNum, nameof(TypeDeclNode), "Invalid type declaration");
        _typeTable.Add(node.Name, type);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ArrayTypeNode node)
    {
        if (node.ElementType.Accept(this) is not LLVMCodeGenVisitorResult.TypeResult { TypeInfo: var elemTypeInfo })
            throw new SemanticException(node.LineNum, nameof(ArrayTypeNode), "Invalid array declaration");
        var arrayType = LLVMTypeRef.CreateArray(elemTypeInfo.LLVMType, (uint)(node.High - node.Low + 1));
        return new LLVMCodeGenVisitorResult.TypeResult(new ArrayTypeInfo(arrayType, elemTypeInfo, node.Low));
    }

    public LLVMCodeGenVisitorResult Visit(CharTypeNode node)
    {
        return new LLVMCodeGenVisitorResult.TypeResult(new CharTypeInfo());
    }

    public LLVMCodeGenVisitorResult Visit(IntegerTypeNode node)
    {
        return new LLVMCodeGenVisitorResult.TypeResult(new IntegerTypeInfo());
    }

    public LLVMCodeGenVisitorResult Visit(RecordTypeNode node)
    {
        var fieldInfos = node.Fields.SelectMany(f =>
        {
            if (f.Type.Accept(this) is not LLVMCodeGenVisitorResult.TypeResult { TypeInfo: var fieldTypeInfo })
                throw new SemanticException(f.LineNum, nameof(RecordTypeNode), "Invalid field type");
            return f.Ids.Select(id => new FieldInfo(id, fieldTypeInfo));
        }).ToList();
        var recordType = LLVMTypeRef.CreateStruct([.. fieldInfos.Select(ft => ft.TypeInfo.LLVMType)], Packed: false);
        return new LLVMCodeGenVisitorResult.TypeResult(new RecordTypeInfo(recordType, fieldInfos));
    }

    public LLVMCodeGenVisitorResult Visit(TypeDefTypeNode node)
    {
        if (_typeTable[node.Identifier] is not (var type, _))
            throw new SemanticException(node.LineNum, nameof(TypeDefTypeNode), $"Unknown type {node.Identifier}");
        return new LLVMCodeGenVisitorResult.TypeResult(type);
    }

    public LLVMCodeGenVisitorResult Visit(VarDeclPartNode node)
    {
        foreach (var varDecl in node.VarDecls)
            varDecl.Accept(this);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(VarDeclNode node)
    {
        if (node.Type.Accept(this) is not LLVMCodeGenVisitorResult.TypeResult { TypeInfo: var typeInfo })
            throw new SemanticException(node.LineNum, nameof(VarDeclNode), $"Invalid var declaration");
        foreach (var id in node.Ids)
        {
            var alloca = _builder.BuildAlloca(typeInfo.LLVMType, id);
            alloca.Name = id;
            _varTable.Add(id, new VarInfo(alloca, typeInfo));
        }
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ProcDeclPartNode node)
    {
        foreach (var procDecl in node.ProcDecls)
            procDecl.Accept(this);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    private static string GetClosureNameForProc(string procName) => $"_closure_{procName}";
    private const string ClosureNamePrev = "_closure_prev";

    public LLVMCodeGenVisitorResult Visit(ProcDeclNode node)
    {
        var (prevProcInfo, prevLocalAllocas) = _varTable.CurrentScope;

        /*
         * struct cur_closure {
         *  prev_closure* _closure_prev;
         *  <prev local allocas>
         * }
         */
        var curClosureStruct = LLVMTypeRef.CreateStruct([
            LLVMTypeRef.CreatePointer(prevProcInfo.ClosureTypeInfo.LLVMType, 0),
            .. prevLocalAllocas.Values.Select(v => LLVMTypeRef.CreatePointer(v.TypeInfo.LLVMType, 0))
        ], Packed: false);

        var curClosureTypeInfo = new RecordTypeInfo(curClosureStruct, [
            new FieldInfo(ClosureNamePrev, prevProcInfo.ClosureTypeInfo),
            .. prevLocalAllocas.Keys.Zip(prevLocalAllocas.Values.Select(v => v.TypeInfo)).Select(t => new FieldInfo(t.First, t.Second))
        ]);

        _typeTable.Add(GetClosureNameForProc(node.Name), curClosureTypeInfo);

        var paramInfos = node.Params.SelectMany(p =>
        {
            if (p.Type.Accept(this) is not LLVMCodeGenVisitorResult.TypeResult { TypeInfo: var typeInfo })
                throw new SemanticException(p.LineNum, nameof(ProcDeclNode), "Invalid procedure parameter type");
            return p.Ids.Select(id => new ParamInfo(id, typeInfo, p.ByRef));
        }).ToList();

        var paramTypes = paramInfos.Select(pi => pi.ByRef
            ? LLVMTypeRef.CreatePointer(pi.TypeInfo.LLVMType, 0)
            : pi.TypeInfo.LLVMType);

        var procType = LLVMTypeRef.CreateFunction(
            LLVMTypeRef.Void,
            [LLVMTypeRef.CreatePointer(curClosureStruct, 0), .. paramTypes], // closure is always by ref
            IsVarArg: false
        );
        var proc = _module.AddFunction(node.Name, procType);
        proc.Linkage = LLVMLinkage.LLVMPrivateLinkage;
        var procInfo = new ProcInfo(proc, procType, _procTable.Depth, curClosureTypeInfo, paramInfos);

        _procTable.Add(node.Name, procInfo);

        using (_typeTable.EnterScope(null))
        using (_varTable.EnterScope(procInfo))
        using (_procTable.EnterScope(null))
        {
            node.TypeDeclPart.Accept(this);

            var entryBlock = proc.AppendBasicBlock("entry");

            _builder.PositionAtEnd(entryBlock); // for parameter localization
            foreach (var p in node.Params) p.Accept(this);

            _builder.PositionAtEnd(entryBlock); // for variable allocation
            node.VarDeclPart.Accept(this);

            node.ProcDeclPart.Accept(this);

            _builder.PositionAtEnd(entryBlock); // for body code
            node.Body.Accept(this);
            _builder.BuildRetVoid();
        }

        if (!proc.VerifyFunction(LLVMVerifierFailureAction.LLVMPrintMessageAction))
            throw new Exception($"Error verifying function");

        _passManager.RunFunctionPassManager(proc);

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    // parameter localization
    public LLVMCodeGenVisitorResult Visit(ParamDeclNode node)
    {
        var procInfo = _varTable.CurrentScope.Extra;
        var index = procInfo.ParamInfos.FindIndex(pi => pi.Name == node.Ids[0]);
        if (index == -1) throw new SemanticException(node.LineNum, nameof(ParamDeclNode), $"Unknown parameter name: {node.Ids[0]}");

        for (int i = 0; i < node.Ids.Length; ++i)
        {
            var name = node.Ids[i];
            var paramInfo = procInfo.ParamInfos[index + i];
            var param = procInfo.LLVMValue.Params[index + i + 1]; // +1 for closure

            param.Name = name;

            LLVMValueRef alloca;
            if (!node.ByRef) // by val, just store it
            {
                alloca = _builder.BuildAlloca(param.TypeOf, node.Ids[i]);
                _builder.BuildStore(param, alloca);
            }
            else alloca = param; // simply pick up the pointer

            _varTable.Add(node.Ids[i], new VarInfo(alloca, paramInfo.TypeInfo));
        }

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(StatementListNode node)
    {
        foreach (var s in node.Statements) s.Accept(this);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(AssignStatementNode node)
    {
        if (node.Right.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var rhs, TypeInfo: var ti, IsLValue: var loadRHS })
            throw new SemanticException(node.LineNum, nameof(AssignStatementNode), "Invalid assignment rhs");

        if (loadRHS) rhs = _builder.BuildLoad2(ti.LLVMType, rhs);

        if (node.Left.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var lhs, IsLValue: true })
            throw new SemanticException(node.LineNum, nameof(AssignStatementNode), "Invalid assignment lhs");

        _builder.BuildStore(rhs, lhs);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(WriteStatementNode node)
    {
        if (node.Expression.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var value, TypeInfo: var ti, IsLValue: var loadValue })
            throw new SemanticException(node.LineNum, nameof(WriteStatementNode), "Invalid write expression");

        if (loadValue) value = _builder.BuildLoad2(ti.LLVMType, value);

        if (ti is CharTypeInfo) // char
        {
            var writeChar = _module.GetNamedFunction("_write_char");
            var writeCharType = LLVMTypeRef.CreateFunction(LLVMTypeRef.Void, [LLVMTypeRef.Int8], IsVarArg: false);
            if (writeChar == null)
            {
                writeChar = _module.AddFunction("_write_char", writeCharType);
                writeChar.Linkage = LLVMLinkage.LLVMExternalLinkage;
            }

            _builder.BuildCall2(writeCharType, writeChar, [value]);
        }
        else if (ti is IntegerTypeInfo) // int
        {
            var writeInt = _module.GetNamedFunction("_write_int");
            var writeIntType = LLVMTypeRef.CreateFunction(LLVMTypeRef.Void, [LLVMTypeRef.Int32], IsVarArg: false);
            if (writeInt == null)
            {
                writeInt = _module.AddFunction("_write_int", writeIntType);
                writeInt.Linkage = LLVMLinkage.LLVMExternalLinkage;
            }

            _builder.BuildCall2(writeIntType, writeInt, [value]);
        }
        else
        {
            throw new SemanticException(node.LineNum, nameof(WriteStatementNode), "Unsupported write type, should be char or integer");
        }

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ReadStatementNode node)
    {
        if (node.Variable.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var alloca, TypeInfo: var ti, IsLValue: true })
            throw new SemanticException(node.LineNum, nameof(ReadStatementNode), "Invalid read variable");

        if (ti is CharTypeInfo) // char
        {
            var readChar = _module.GetNamedFunction("_read_char");
            var readCharType = LLVMTypeRef.CreateFunction(LLVMTypeRef.Int8, [], IsVarArg: false);
            if (readChar == null)
            {
                readChar = _module.AddFunction("_read_char", readCharType);
                readChar.Linkage = LLVMLinkage.LLVMExternalLinkage;
            }

            var readCharResult = _builder.BuildCall2(readCharType, readChar, []);
            _builder.BuildStore(readCharResult, alloca);
        }
        else if (ti is IntegerTypeInfo) // int
        {
            var readInt = _module.GetNamedFunction("_read_int");
            var readIntType = LLVMTypeRef.CreateFunction(LLVMTypeRef.Int32, [], IsVarArg: false);
            if (readInt == null)
            {
                readInt = _module.AddFunction("_read_int", readIntType);
                readInt.Linkage = LLVMLinkage.LLVMExternalLinkage;
            }

            var readIntResult = _builder.BuildCall2(readIntType, readInt, []);
            _builder.BuildStore(readIntResult, alloca);
        }
        else
        {
            throw new SemanticException(node.LineNum, nameof(ReadStatementNode), "Unsupported read type, should be char or integer");
        }

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    private int _ifCounter = 0;

    // Since 'if' is statement instead of expression in SNL,
    // no phi node is needed for the merge block :)
    public LLVMCodeGenVisitorResult Visit(IfStatementNode node)
    {
        var ifCounter = _ifCounter++;

        if (node.Condition.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var condition, IsLValue: var loadCondition })
            throw new SemanticException(node.LineNum, nameof(IfStatementNode), "Invalid if condition");

        if (loadCondition) condition = _builder.BuildLoad2(condition.TypeOf.ElementType, condition, $"if_cond_{ifCounter}");

        var proc = _builder.InsertBlock.Parent;

        var thenBlock = proc.AppendBasicBlock($"then_{ifCounter}");
        var elseBlock = LLVMBasicBlockRef.CreateInContext(_module.Context, $"else_{ifCounter}");
        var mergeBlock = LLVMBasicBlockRef.CreateInContext(_module.Context, $"if_merge_{ifCounter}");

        _builder.BuildCondBr(condition, thenBlock, elseBlock);

        _builder.PositionAtEnd(thenBlock);
        node.Then.Accept(this);
        _builder.BuildBr(mergeBlock);

        LLVM.AppendExistingBasicBlock(proc, elseBlock);
        _builder.PositionAtEnd(elseBlock);
        node.Else.Accept(this);
        _builder.BuildBr(mergeBlock);

        LLVM.AppendExistingBasicBlock(proc, mergeBlock);
        _builder.PositionAtEnd(mergeBlock);

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(CallStatementNode node)
    {
        if (_procTable[node.Name] is not (var calleeInfo, _))
            throw new SemanticException(node.LineNum, nameof(CallStatementNode), $"Unknown procedure {node.Name}");

        var (curProcInfo, _) = _varTable.CurrentScope;
        var calleeClosureTypeInfo = calleeInfo.ClosureTypeInfo;

        LLVMValueRef calleeClosurePtr;

        // L call L + 1, create new closure
        if (curProcInfo.Level == calleeInfo.Level - 1)
        {
            calleeClosurePtr = _builder.BuildAlloca(calleeClosureTypeInfo.LLVMType, "closure");

            // not _start
            if (curProcInfo.LLVMValue.Params.Length > 0)
            {
                var prevClosureGEP = _builder.BuildGEP2(calleeClosureTypeInfo.LLVMType, calleeClosurePtr, [
                    LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0),
                    LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0)
                ]);

                _builder.BuildStore(curProcInfo.LLVMValue.Params[0], prevClosureGEP);
            }

            for (int i = 1; i < calleeClosureTypeInfo.FieldInfos.Count; ++i)
            {
                var fi = calleeClosureTypeInfo.FieldInfos[i];
                if (_varTable[fi.Name] is not (var varInfo, var procInfo))
                    throw new Exception($"{nameof(CallStatementNode)}: Could not find closure variable {fi.Name}");

                // how
                if (procInfo != curProcInfo)
                    throw new Exception($"{nameof(CallStatementNode)}: Variable {fi.Name} is not in the current procedure");

                var varPtrGEP = _builder.BuildGEP2(calleeClosureTypeInfo.LLVMType, calleeClosurePtr, [
                    LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0),
                    LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, (ulong)i)
                ]);

                _builder.BuildStore(varInfo.LLVMValue, varPtrGEP);
            }
        }
        else
        {
            // L call L - n, where n >= 0, use existing closure
            // while not on the same level, get the upper closure
            var curClosureTypeInfo = curProcInfo.ClosureTypeInfo;
            var curClosurePtr = curProcInfo.LLVMValue.Params[0];
            for (int level = curProcInfo.Level; level > calleeInfo.Level; --level)
            {
                var prevClosureGEP = _builder.BuildStructGEP2(curProcInfo.ClosureTypeInfo.LLVMType, curClosurePtr, 0);
                curClosurePtr = _builder.BuildLoad2(LLVMTypeRef.CreatePointer(curClosureTypeInfo!.FieldInfos[0].TypeInfo.LLVMType, 0), prevClosureGEP);
                curClosureTypeInfo = curClosureTypeInfo.FieldInfos[0].TypeInfo as RecordTypeInfo;
            }
            calleeClosurePtr = curClosurePtr;
        }

        var args = node.Arguments.Zip(calleeInfo.ParamInfos).Select(pair =>
        {
            var (argExpr, paramInfo) = pair;

            if (argExpr.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var arg, TypeInfo: var ti, IsLValue: var isLValue })
                throw new SemanticException(argExpr.LineNum, nameof(CallStatementNode), $"Invalid argument expression for {paramInfo.Name}");

            if (ti.LLVMType != paramInfo.TypeInfo.LLVMType)
                throw new SemanticException(argExpr.LineNum, nameof(CallStatementNode), $"Argument type mismatch for {paramInfo.Name}");

            if (paramInfo.ByRef && !isLValue)
                throw new SemanticException(argExpr.LineNum, nameof(CallStatementNode), $"Argument {paramInfo.Name} must be an lvalue");

            if (!paramInfo.ByRef && isLValue)
                arg = _builder.BuildLoad2(ti.LLVMType, arg);

            return arg;
        });

        _builder.BuildCall2(calleeInfo.ProcType, calleeInfo.LLVMValue, [calleeClosurePtr, .. args]);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    private int _whileCounter = 0;
    public LLVMCodeGenVisitorResult Visit(WhileStatementNode node)
    {
        var whileCounter = _whileCounter++;
        var proc = _builder.InsertBlock.Parent;

        var condBlock = proc.AppendBasicBlock($"while_cond_{whileCounter}");
        _builder.BuildBr(condBlock);

        _builder.PositionAtEnd(condBlock);
        if (node.Condition.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var cond, TypeInfo: var condTypeInfo, IsLValue: var loadCondition })
            throw new SemanticException(node.Condition.LineNum, nameof(WhileStatementNode), "Invalid while condition");
        if (loadCondition) cond = _builder.BuildLoad2(condTypeInfo.LLVMType, cond, $"while_cond_val_{whileCounter}");

        var bodyBlock = LLVMBasicBlockRef.CreateInContext(_module.Context, $"while_body_{whileCounter}");
        var mergeBlock = LLVMBasicBlockRef.CreateInContext(_module.Context, $"while_merge{whileCounter}");
        _builder.BuildCondBr(cond, bodyBlock, mergeBlock);

        LLVM.AppendExistingBasicBlock(proc, bodyBlock);
        _builder.PositionAtEnd(bodyBlock);
        node.Body.Accept(this);
        _builder.BuildBr(condBlock);

        LLVM.AppendExistingBasicBlock(proc, mergeBlock);
        _builder.PositionAtEnd(mergeBlock);

        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ReturnStatementNode node)
    {
        var proc = _builder.InsertBlock.Parent;
        _builder.BuildRetVoid();
        var retContBlock = proc.AppendBasicBlock("return_cont");
        _builder.PositionAtEnd(retContBlock);
        return new LLVMCodeGenVisitorResult.VoidResult();
    }

    public LLVMCodeGenVisitorResult Visit(ArrayMemberExpressionNode node)
    {
        if (node.Array.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var array, TypeInfo: ArrayTypeInfo ti, IsLValue: true })
            throw new SemanticException(node.Array.LineNum, nameof(ArrayMemberExpressionNode), "Invalid array expression");

        if (node.Index.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var index, TypeInfo: IntegerTypeInfo, IsLValue: var loadIndex })
            throw new SemanticException(node.Index.LineNum, nameof(ArrayMemberExpressionNode), "Invalid array index expression");

        if (loadIndex) index = _builder.BuildLoad2(LLVMTypeRef.Int32, index, "arr_idx");

        index = _builder.BuildSub(index, LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, (ulong)ti.Low), "arr_idx_sub_low");
        var elementPtr = _builder.BuildGEP2(ti.LLVMType, array, [LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0), index], "arr_elem_ptr".AsSpan());
        return new LLVMCodeGenVisitorResult.ValueResult(elementPtr, ti.ElementTypeInfo, IsLValue: true);
    }

    public LLVMCodeGenVisitorResult Visit(RecordMemberExpressionNode node)
    {
        if (node.Record.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var record, TypeInfo: RecordTypeInfo ti, IsLValue: true })
            throw new SemanticException(node.Record.LineNum, nameof(RecordMemberExpressionNode), "Invalid record expression");

        if (ti.FieldInfos.FindIndex(f => f.Name == node.Member.Name) is var index && index < 0)
            throw new SemanticException(node.Member.LineNum, nameof(RecordMemberExpressionNode), $"Unknown record member {node.Member.Name}");

        var fieldInfo = ti.FieldInfos[index];
        var fieldPtr = _builder.BuildGEP2(ti.LLVMType, record, [LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0), LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, (uint)index)]);
        return new LLVMCodeGenVisitorResult.ValueResult(fieldPtr, fieldInfo.TypeInfo, IsLValue: true);
    }

    public LLVMCodeGenVisitorResult Visit(BinaryExpressionNode node)
    {
        if (node.Left.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var lhs, TypeInfo: var lhsTypeInfo, IsLValue: var loadLHS })
            throw new SemanticException(node.Left.LineNum, nameof(BinaryExpressionNode), "Invalid binary expression lhs");

        if (loadLHS) lhs = _builder.BuildLoad2(lhsTypeInfo.LLVMType, lhs);

        if (node.Right.Accept(this) is not LLVMCodeGenVisitorResult.ValueResult { Value: var rhs, TypeInfo: var rhsTypeInfo, IsLValue: var loadRHS })
            throw new SemanticException(node.Right.LineNum, nameof(BinaryExpressionNode), "Invalid binary expression rhs");

        if (loadRHS) rhs = _builder.BuildLoad2(rhsTypeInfo.LLVMType, rhs);

        LLVMValueRef result = node.Operator switch
        {
            Operator.Add => _builder.BuildAdd(lhs, rhs),
            Operator.Sub => _builder.BuildSub(lhs, rhs),
            Operator.Mul => _builder.BuildMul(lhs, rhs),
            Operator.Lt => _builder.BuildICmp(LLVMIntPredicate.LLVMIntSLT, lhs, rhs),
            _ => throw new SemanticException(node.LineNum, nameof(BinaryExpressionNode), $"Unsupported operator {node.Operator}")
        };

        return new LLVMCodeGenVisitorResult.ValueResult(result, node.Operator switch
        {
            Operator.Add => lhsTypeInfo,
            Operator.Sub => lhsTypeInfo,
            Operator.Mul => lhsTypeInfo,
            Operator.Lt => new BooleanTypeInfo(),
            _ => throw new SemanticException(node.LineNum, nameof(BinaryExpressionNode), $"Unsupported operator {node.Operator}")
        }, IsLValue: false);
    }

    public LLVMCodeGenVisitorResult Visit(ConstantIntExpressionNode node)
    {
        return new LLVMCodeGenVisitorResult.ValueResult(
            LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, (ulong)node.Value, SignExtend: true),
            new IntegerTypeInfo(),
            IsLValue: false
        );
    }

    public LLVMCodeGenVisitorResult Visit(ConstantCharExpressionNode node)
    {
        return new LLVMCodeGenVisitorResult.ValueResult(
            LLVMValueRef.CreateConstInt(LLVMTypeRef.Int8, (ulong)node.Value, SignExtend: false),
            new CharTypeInfo(),
            IsLValue: false
        );
    }

    public LLVMCodeGenVisitorResult Visit(IdentifierExpressionNode node)
    {
        if (_varTable[node.Name] is not (VarInfo varInfo, ProcInfo procInfo))
            throw new SemanticException(node.LineNum, nameof(IdentifierExpressionNode), $"Could not find variable {node.Name}");

        var curProcInfo = _varTable.CurrentScope.Extra;

        if (curProcInfo == procInfo)
            return new LLVMCodeGenVisitorResult.ValueResult(varInfo.LLVMValue, varInfo.TypeInfo, IsLValue: true);

        var closurePtr = curProcInfo.LLVMValue.Params[0]; // closure is always the first parameter
        var closureTypeInfo = curProcInfo.ClosureTypeInfo;

        // recursively getting the parent closure, until we reach the closure directly containing the variable
        while (closureTypeInfo.FieldInfos[0].TypeInfo != procInfo.ClosureTypeInfo)
        {
            var prevClosureGEP = _builder.BuildGEP2(closureTypeInfo.LLVMType, closurePtr, [LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0), LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0)]);
            closurePtr = _builder.BuildLoad2(LLVMTypeRef.CreatePointer(closureTypeInfo.FieldInfos[0].TypeInfo.LLVMType, 0), prevClosureGEP);

            // not likely to happen
            if (closureTypeInfo.FieldInfos[0].TypeInfo is not RecordTypeInfo prevClosureTypeInfo)
                throw new Exception($"{nameof(IdentifierExpressionNode)}: Closure type info is not record type info");

            closureTypeInfo = prevClosureTypeInfo;
        }

        var varIndex = closureTypeInfo.FieldInfos.FindIndex(f => f.Name == node.Name);
        if (varIndex < 0) throw new SemanticException(node.LineNum, nameof(IdentifierExpressionNode), $"Could not find variable {node.Name}");

        var varPtrGEP = _builder.BuildGEP2(closureTypeInfo.LLVMType, closurePtr, [LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, 0), LLVMValueRef.CreateConstInt(LLVMTypeRef.Int32, (uint)varIndex)]);
        var varPtr = _builder.BuildLoad2(LLVMTypeRef.CreatePointer(closureTypeInfo.FieldInfos[varIndex].TypeInfo.LLVMType, 0), varPtrGEP);
        return new LLVMCodeGenVisitorResult.ValueResult(varPtr, closureTypeInfo.FieldInfos[varIndex].TypeInfo, IsLValue: true);
    }
}
