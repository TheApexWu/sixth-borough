"""Recompact borough JSONs: reduce coord precision + simplify polygons.

Reduces ~262 MB → ~140-160 MB with zero visual difference at map zoom levels.
- Coordinates: 6 decimal → 5 decimal (1.1m accuracy, sufficient for building-scale)
- Polygons: Douglas-Peucker simplification for buildings with >16 vertices
- Heights: round to 1 decimal
"""

import json
import math
import os
import sys

def douglas_peucker(points, epsilon):
    """Simplify polygon with Douglas-Peucker algorithm."""
    if len(points) <= 4:
        return points

    dmax = 0
    index = 0
    end = len(points) - 1

    for i in range(1, end):
        d = perpendicular_distance(points[i], points[0], points[end])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        left = douglas_peucker(points[:index + 1], epsilon)
        right = douglas_peucker(points[index:], epsilon)
        return left[:-1] + right
    else:
        return [points[0], points[end]]

def perpendicular_distance(point, line_start, line_end):
    """Distance from point to line segment."""
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    if dx == 0 and dy == 0:
        return math.sqrt((point[0] - line_start[0])**2 + (point[1] - line_start[1])**2)
    t = ((point[0] - line_start[0]) * dx + (point[1] - line_start[1]) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    proj_x = line_start[0] + t * dx
    proj_y = line_start[1] + t * dy
    return math.sqrt((point[0] - proj_x)**2 + (point[1] - proj_y)**2)

def recompact(buildings, epsilon=0.00001):
    """Recompact building list: reduce precision + simplify polygons."""
    out = []
    for b in buildings:
        p = b.get('p', [])
        # Simplify if complex
        if len(p) > 16:
            p = douglas_peucker(p, epsilon)
            # Ensure polygon is closed
            if p and p[0] != p[-1]:
                p.append(p[0])
        # Reduce coordinate precision to 5 decimals
        p = [[round(c[0], 5), round(c[1], 5)] for c in p]
        entry = {
            'p': p,
            'h': round(b.get('h', 0), 1),
        }
        if b.get('y'):
            entry['y'] = b['y']
        if b.get('b'):
            entry['b'] = b['b']
        out.append(entry)
    return out

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    boroughs = ['manhattan', 'bronx', 'brooklyn', 'queens', 'staten']

    for boro in boroughs:
        src = os.path.join(data_dir, f'{boro}_compact.json')
        if not os.path.exists(src):
            print(f'  SKIP {boro} (not found)')
            continue

        orig_size = os.path.getsize(src) / 1e6
        with open(src) as f:
            data = json.load(f)

        recompacted = recompact(data)

        # Write with minimal whitespace
        with open(src, 'w') as f:
            json.dump(recompacted, f, separators=(',', ':'))

        new_size = os.path.getsize(src) / 1e6
        pct = (1 - new_size / orig_size) * 100
        print(f'  {boro}: {len(data):,} buildings, {orig_size:.1f} MB → {new_size:.1f} MB ({pct:.0f}% smaller)')

if __name__ == '__main__':
    main()
