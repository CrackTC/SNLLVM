namespace Sorac.SNL.Utils;

public class ScopedDictionary<TKey, TValue, TScopeExtra> where TKey : notnull
{
    private readonly Stack<(TScopeExtra Extra, OrderedDictionary<TKey, TValue> Dict)> _scopeStack = [];

    public (TScopeExtra Extra, OrderedDictionary<TKey, TValue> Dict) CurrentScope => _scopeStack.Peek();

    public IDisposable EnterScope(TScopeExtra extra) => new Scope(this, extra);

    public (TValue, TScopeExtra)? this[TKey key]
    {
        get
        {
            foreach (var (extra, dict) in _scopeStack)
                if (dict.TryGetValue(key, out var value))
                    return (value, extra);
            return null;
        }
    }

    public void Add(TKey key, TValue value)
    {
        if (_scopeStack.Count == 0) throw new InvalidOperationException("No scope to add to");
        _scopeStack.Peek().Dict.Add(key, value);
    }

    public int Depth => _scopeStack.Count;

    private class Scope : IDisposable
    {
        private readonly ScopedDictionary<TKey, TValue, TScopeExtra> _parent;
        private readonly TScopeExtra _extra;

        public Scope(ScopedDictionary<TKey, TValue, TScopeExtra> parent, TScopeExtra extra)
        {
            _parent = parent;
            _extra = extra;
            _parent._scopeStack.Push((_extra, []));
        }

        public void Dispose() => _parent._scopeStack.Pop();
    }
}
