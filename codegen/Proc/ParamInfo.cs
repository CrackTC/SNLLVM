using Sorac.SNL.Type;

namespace Sorac.SNL.Proc;

public record class ParamInfo(string Name, TypeInfo TypeInfo, bool ByRef);
