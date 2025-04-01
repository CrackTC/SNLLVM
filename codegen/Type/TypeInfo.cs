using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public abstract record class TypeInfo(LLVMTypeRef LLVMType);
