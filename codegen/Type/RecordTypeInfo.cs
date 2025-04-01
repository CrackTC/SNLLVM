using LLVMSharp.Interop;

namespace Sorac.SNL.Type;

public record class FieldInfo(string Name, TypeInfo TypeInfo);

public record class RecordTypeInfo(LLVMTypeRef LLVMType, List<FieldInfo> FieldInfos) : TypeInfo(LLVMType);
