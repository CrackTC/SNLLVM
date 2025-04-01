using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public record class CharTypeInfo() : TypeInfo(LLVMTypeRef.Int8);
