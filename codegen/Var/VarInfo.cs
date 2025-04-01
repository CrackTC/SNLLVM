using LLVMSharp.Interop;
using Sorac.SNL.Type;

namespace Sorac.SNL.Var;

public record class VarInfo(LLVMValueRef LLVMValue, TypeInfo TypeInfo);
