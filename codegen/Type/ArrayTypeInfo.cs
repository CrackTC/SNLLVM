using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public record class ArrayTypeInfo(LLVMTypeRef LLVMType, TypeInfo ElementTypeInfo, int Low) : TypeInfo(LLVMType);
