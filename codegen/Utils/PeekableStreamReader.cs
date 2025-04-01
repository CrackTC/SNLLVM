namespace Sorac.SNL.Utils;

public class PeekableStreamReader
{
    private StreamReader Underlying;
    private Queue<string> BufferedLines;

    public PeekableStreamReader(StreamReader underlying)
    {
        Underlying = underlying;
        BufferedLines = new Queue<string>();
    }

    public string? PeekLine()
    {
        if (BufferedLines.Count > 0)
            return BufferedLines.Peek();
        var line = Underlying.ReadLine();
        if (line == null)
            return null;
        BufferedLines.Enqueue(line);
        return line;
    }


    public string? ReadLine()
    {
        if (BufferedLines.Count > 0)
            return BufferedLines.Dequeue();
        return Underlying.ReadLine();
    }
}
