using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public class Stone
{
    public (Int64, Int64, Int64) Position { get; }
    public (Int64, Int64, Int64) Velocity { get; }

    public Stone((Int64, Int64, Int64) position, (Int64, Int64, Int64) velocity)
    {
        Position = position;
        Velocity = velocity;
    }

    public override string ToString()
    {
        return $"{Position} @{Velocity}";
    }

    public static Stone ParseLine(string line)
    {
        var parts = line.Replace(" @ ", ", ").Split(", ").Select(Int64.Parse).ToArray();
        return new Stone((parts[0], parts[1], parts[2]), (parts[3], parts[4], parts[5]));
    }
}

public class Hail
{
    private List<Stone> Stones { get; } = new List<Stone>();

    public Hail(string filePath)
    {
        LoadFromFile(filePath);
    }

    public void Solve()
    {
        Parallel.For(-600, 601, (vx, state) =>
        {
            Console.WriteLine($"Checking vx={vx}");
            for (Int64 vy = -600; vy <= 600; vy++)
            {
                for (Int64 vz = -200; vz <= 600; vz++)
                {
                    if (PointFits((vx, vy, vz)))
                    {
                        state.Stop();
                        return;
                    }
                }
            }
        });
        Console.WriteLine("All solutions checked, not found");
    }

    private bool PointFits((Int64, Int64, Int64) v)
    {
        var p = FindPoint(v);
        if (p == null)
        {
            return false;
        }

        foreach (var stone in Stones)
        {
            Int64 t_d = v.Item1 - stone.Velocity.Item1;
            if (t_d == 0)
            {
                return false;
            }
            Int64 t = (stone.Position.Item1 - p.Value.Item1) / t_d;

            if (p.Value.Item2 + v.Item2 * t != stone.Position.Item2 + stone.Velocity.Item2 * t ||
                p.Value.Item3 + v.Item3 * t != stone.Position.Item3 + stone.Velocity.Item3 * t)
            {
                return false;
            }
        }

        Console.WriteLine($"Found a solution: p={p} @ v={v}");
        return true;
    }

    private (Int64, Int64, Int64)? FindPoint((Int64, Int64, Int64) r)
    {
        var a = Stones[0];
        var b = Stones[1];

        Int64 dx1 = r.Item1 - a.Velocity.Item1;
        if (dx1 == 0)
        {
            return null;
        }

        double k1 = a.Velocity.Item2 / (double)dx1 - r.Item2 / (double)dx1;
        double b1 = a.Position.Item2 + a.Velocity.Item2 * a.Position.Item1 / (double)dx1 - r.Item2 * a.Position.Item1 / (double)dx1;

        double k2 = a.Velocity.Item3 / (double)dx1 - r.Item3 / (double)dx1;
        double b2 = a.Position.Item3 + a.Velocity.Item3 * a.Position.Item1 / (double)dx1 - r.Item3 * a.Position.Item1 / (double)dx1;

        dx1 = r.Item1 - b.Velocity.Item1;
        if (dx1 == 0)
        {
            return null;
        }

        double k3 = b.Velocity.Item2 / (double)dx1 - r.Item2 / (double)dx1;
        double b3 = b.Position.Item2 + b.Velocity.Item2 * b.Position.Item1 / (double)dx1 - r.Item2 * b.Position.Item1 / (double)dx1;

        double x_denom = k3 - k1;
        if (x_denom == 0)
        {
            return null;
        }

        double x = (b3 - b1) / x_denom;
        double y = b1 - k1 * x;
        double z = b2 - k2 * x;

        return ((Int64)Math.Round(x), (Int64)Math.Round(y), (Int64)Math.Round(z));
    }

    private void LoadFromFile(string filePath)
    {
        foreach (var line in File.ReadAllLines(filePath))
        {
            Stones.Add(Stone.ParseLine(line));
        }
    }
}

public static class Program
{
    public static void Main(string[] args)
    {
        // this worked ~10 seconds
        var hail = new Hail("/Users/andreisitaev/Downloads/input_d24.txt");
        hail.Solve();
    }
}