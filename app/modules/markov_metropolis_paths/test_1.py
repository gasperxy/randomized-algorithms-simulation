import sys
from math import prod

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    p_pct = int(next(it))

    p = p_pct / 100.0
    q = 1.0 - p

    # w[i][j] = število vzporednih povezav med i<j (zanke ignoriramo)
    w = [[0] * n for _ in range(n)]
    for _ in range(m):
        u = int(next(it)) - 1
        v = int(next(it)) - 1
        if u == v:
            continue  # zanka ne vpliva na povezanost
        if u > v:
            u, v = v, u
        w[u][v] += 1

    N = 1 << n

    # internalE[mask] = vsota multiplicitete povezav z obema krajiščema v mask (brez zank)
    internalE = [0] * N
    for mask in range(1, N):
        b = (mask & -mask).bit_length() - 1
        pmask = mask & (mask - 1)
        add = 0
        j = pmask
        while j:
            v = (j & -j).bit_length() - 1
            a, c = (b, v) if b < v else (v, b)
            add += w[a][c]
            j &= j - 1
        internalE[mask] = internalE[pmask] + add

    maxE = internalE[N - 1]
    qpow = [1.0] * (maxE + 1)
    for i in range(1, maxE + 1):
        qpow[i] = qpow[i - 1] * q

    conn = [0.0] * N
    for mask in range(1, N):
        # ena točka -> povezan
        if mask & (mask - 1) == 0:
            conn[mask] = 1.0
            continue

        r = (mask & -mask).bit_length() - 1  # sidro: najmanjši bit
        s = 0.0

        sub = (mask - 1) & mask
        while sub:
            if (sub >> r) & 1:  # mora vsebovati sidro
                other = mask ^ sub
                cutE = internalE[mask] - internalE[sub] - internalE[other]
                s += conn[sub] * qpow[cutE]
            sub = (sub - 1) & mask

        val = 1.0 - s
        if val < 0.0:
            val = 0.0
        elif val > 1.0:
            val = 1.0
        conn[mask] = val

    # dovolj natančno za 1e-6
    sys.stdout.write(f"{conn[N - 1]:.10f}\n")

if __name__ == "__main__":
    main()