using LLVMSharp.Interop;
using Sorac.SNL.Type;

namespace Sorac.SNL.Proc;

public record class ProcInfo(LLVMValueRef LLVMValue, LLVMTypeRef ProcType, int Level, RecordTypeInfo ClosureTypeInfo, List<ParamInfo> ParamInfos);
