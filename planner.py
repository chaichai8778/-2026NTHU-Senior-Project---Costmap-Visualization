import math
import heapq

def _heuristic(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

_NEIGHBORS = [
    (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
    (1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2)), 
    (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2))
]

def _is_blocked(cell, inflation_map):
    if inflation_map.get(cell, 0) > 0:
        return True
    return False

def _nearest_free(inflation_map, col, row, radius=15):
    for r in range(radius):
        for dc in range(-r, r+1):
            for dr in range(-r, r+1):
                nc, nr = col + dc, row + dr
                if not _is_blocked((nc, nr), inflation_map):
                    return (nc, nr)
    return None

def _los( inflation_map, a, b):
    ac, ar = a
    bc, br = b
    dc, dr = abs(bc - ac), abs(br - ar)
    sc = 1 if ac < bc else -1
    sr = 1 if ar < br else -1
    err = dc - dr
    cc, cr = ac, ar
    
    while True:
        if _is_blocked((cc, cr), inflation_map):
            return False
        if cc == bc and cr == br:
            return True
        e2 = 2 * err
        if e2 > -dr:
            err -= dr
            cc += sc
        if e2 < dc:
            err += dc 
            cr += sr

def _smooth(path, inflation_map):
    if not path or len(path) < 16:
        return path
    smoothed = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            if _los(inflation_map, path[i], path[j]):
                break
            j -= 1
        smoothed.append(path[j])
        i = j
    return smoothed

def astar(start, goal,inflation_map):
    fallback_path = [start, start]

    # 1. 檢查終點是否安全，若不安全則修正到最近的淨空格 
    if _is_blocked(goal, inflation_map):
        replaced_goal = _nearest_free(inflation_map, goal[0], goal[1])
        if replaced_goal is None:
            print("[A* WARNING] 目標點位於障礙區，且周圍搜尋範圍內無安全空地！")
            return fallback_path # 找不到替代點，安全返回原地
        goal = replaced_goal

    if _is_blocked(start, inflation_map):
        print("[A* WARNING] 小車目前處於膨脹危險區內，規劃停止以策安全！")
        return fallback_path

    open_heap = []
    heapq.heappush(open_heap, (0.0, start))
    
    came_from = {}
    g_score = {start: 0.0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            
            return _smooth(path, inflation_map)

        cc, cr = current
        current_g = g_score[current]

        for dx, dy, cost in _NEIGHBORS:
            neighbor = (cc + dx, cr + dy)
            
            if _is_blocked(neighbor, inflation_map):
                continue
            
            tentative_g = current_g + cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + _heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, neighbor))

    print("[A* WARNING] 路徑被完全阻斷，找不到可行路徑！")
    return fallback_path