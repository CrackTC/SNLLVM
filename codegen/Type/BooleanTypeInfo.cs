using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public record class BooleanTypeInfo() : TypeInfo(LLVMTypeRef.Int1);