using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public record class IntegerTypeInfo() : TypeInfo(LLVMTypeRef.Int32);
