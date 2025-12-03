# LeetCode图论算法专题

## 📚 简介

图论是计算机科学中的一个重要分支，研究图(Graph)这种数据结构及其相关算法。在LeetCode中，图论问题占据了相当大的比重，涉及到图的遍历、最短路径、最小生成树、拓扑排序等多个方面。

## 🎯 学习目标

- 理解图的基本概念和表示方法
- 掌握图的遍历算法(BFS、DFS)
- 熟练运用最短路径算法(Dijkstra、Bellman-Ford、Floyd)
- 理解最小生成树算法(Prim、Kruskal)
- 掌握拓扑排序及其应用
- 能够识别和解决各类图论问题

## 📘 图的基本概念

### 图的定义
图G由顶点(Vertex)集合V和边(Edge)集合E组成，记作G=(V,E)。

### 图的分类
1. **有向图**：边有方向性
2. **无向图**：边无方向性
3. **有权图**：边带有权重
4. **无权图**：边没有权重

### 图的表示方法
1. **邻接矩阵**：使用二维数组表示顶点间的关系
2. **邻接表**：使用链表或数组列表表示每个顶点的邻居

## 🗂️ 图论算法分类

### 1. 图的遍历

图的遍历是图论算法的基础，主要包括广度优先搜索(BFS)和深度优先搜索(DFS)。

#### 广度优先搜索(BFS)

##### 基本思想
从起始顶点开始，逐层向外扩展，先访问离起始顶点近的顶点，再访问远的顶点。

##### 应用场景
1. 最短路径问题(无权图)
2. 层序遍历
3. 连通性检测

##### 经典例题
1. [二叉树的层序遍历](https://leetcode.com/problems/binary-tree-level-order-traversal/)
2. [岛屿数量](https://leetcode.com/problems/number-of-islands/)
3. [打开转盘锁](https://leetcode.com/problems/open-the-lock/)
4. [单词接龙](https://leetcode.com/problems/word-ladder/)
5. [最小基因变化](https://leetcode.com/problems/minimum-genetic-mutation/)

##### 代码模板

```java
import java.util.*;

// BFS通用模板
public void bfsTemplate(Graph graph, int start) {
    Queue<Integer> queue = new LinkedList<>();
    Set<Integer> visited = new HashSet<>();
    
    queue.offer(start);
    visited.add(start);
    
    while (!queue.isEmpty()) {
        int size = queue.size();
        
        for (int i = 0; i < size; i++) {
            int node = queue.poll();
            // 处理当前节点
            
            for (int neighbor : graph.getNeighbors(node)) {
                if (!visited.contains(neighbor)) {
                    queue.offer(neighbor);
                    visited.add(neighbor);
                }
            }
        }
    }
}

// 岛屿数量
public int numIslands(char[][] grid) {
    if (grid == null || grid.length == 0) return 0;
    
    int rows = grid.length;
    int cols = grid[0].length;
    int count = 0;
    
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (grid[i][j] == '1') {
                bfs(grid, i, j);
                count++;
            }
        }
    }
    
    return count;
}

private void bfs(char[][] grid, int row, int col) {
    int[][] directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
    Queue<int[]> queue = new LinkedList<>();
    
    queue.offer(new int[]{row, col});
    grid[row][col] = '0'; // 标记为已访问
    
    while (!queue.isEmpty()) {
        int[] current = queue.poll();
        int r = current[0];
        int c = current[1];
        
        for (int[] dir : directions) {
            int nr = r + dir[0];
            int nc = c + dir[1];
            
            if (nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length && grid[nr][nc] == '1') {
                queue.offer(new int[]{nr, nc});
                grid[nr][nc] = '0'; // 标记为已访问
            }
        }
    }
}
```

#### 深度优先搜索(DFS)

##### 基本思想
从起始顶点开始，沿着一条路径尽可能深入地访问顶点，直到无法继续为止，然后回溯到上一个顶点，继续探索其他路径。

##### 应用场景
1. 连通性检测
2. 路径问题
3. 拓扑排序
4. 强连通分量

##### 经典例题
1. [岛屿数量](https://leetcode.com/problems/number-of-islands/)
2. [岛屿的最大面积](https://leetcode.com/problems/max-area-of-island/)
3. [被围绕的区域](https://leetcode.com/problems/surrounded-regions/)
4. [太平洋大西洋水流问题](https://leetcode.com/problems/pacific-atlantic-water-flow/)
5. [课程表](https://leetcode.com/problems/course-schedule/)

##### 代码模板

```java
// DFS通用模板 - 递归
public void dfsTemplate(Graph graph, int node, Set<Integer> visited) {
    visited.add(node);
    // 处理当前节点
    
    for (int neighbor : graph.getNeighbors(node)) {
        if (!visited.contains(neighbor)) {
            dfsTemplate(graph, neighbor, visited);
        }
    }
}

// DFS通用模板 - 迭代
public void dfsIterative(Graph graph, int start) {
    Stack<Integer> stack = new Stack<>();
    Set<Integer> visited = new HashSet<>();
    
    stack.push(start);
    
    while (!stack.isEmpty()) {
        int node = stack.pop();
        
        if (!visited.contains(node)) {
            visited.add(node);
            // 处理当前节点
            
            for (int neighbor : graph.getNeighbors(node)) {
                if (!visited.contains(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }
    }
}

// 岛屿的最大面积
public int maxAreaOfIsland(int[][] grid) {
    if (grid == null || grid.length == 0) return 0;
    
    int maxArea = 0;
    
    for (int i = 0; i < grid.length; i++) {
        for (int j = 0; j < grid[0].length; j++) {
            if (grid[i][j] == 1) {
                maxArea = Math.max(maxArea, dfs(grid, i, j));
            }
        }
    }
    
    return maxArea;
}

private int dfs(int[][] grid, int row, int col) {
    if (row < 0 || row >= grid.length || col < 0 || col >= grid[0].length || grid[row][col] == 0) {
        return 0;
    }
    
    grid[row][col] = 0; // 标记为已访问
    
    return 1 + dfs(grid, row + 1, col) + dfs(grid, row - 1, col) 
             + dfs(grid, row, col + 1) + dfs(grid, row, col - 1);
}
```

### 2. 最短路径算法

最短路径问题是图论中的经典问题，目标是找到图中两点之间的最短路径。

#### Dijkstra算法

##### 基本思想
适用于非负权重图的单源最短路径问题，通过贪心策略逐步确定起点到各顶点的最短距离。

##### 应用场景
1. 网络路由
2. 地图导航
3. 游戏AI寻路

##### 经典例题
1. [网络延迟时间](https://leetcode.com/problems/network-delay-time/)
2. [路径中的最大概率](https://leetcode.com/problems/path-with-maximum-probability/)
3. [雇佣K名工人的最低成本](https://leetcode.com/problems/minimum-cost-to-hire-k-workers/)

##### 代码模板

```java
import java.util.*;

// Dijkstra算法模板
public int dijkstra(int n, int[][] edges, int start, int end) {
    // 构建邻接表
    Map<Integer, List<int[]>> graph = new HashMap<>();
    for (int[] edge : edges) {
        graph.computeIfAbsent(edge[0], k -> new ArrayList<>()).add(new int[]{edge[1], edge[2]});
        graph.computeIfAbsent(edge[1], k -> new ArrayList<>()).add(new int[]{edge[0], edge[2]});
    }
    
    // 距离数组
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[start] = 0;
    
    // 优先队列，按距离排序
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
    pq.offer(new int[]{start, 0});
    
    while (!pq.isEmpty()) {
        int[] current = pq.poll();
        int node = current[0];
        int distance = current[1];
        
        // 如果已经找到了更短的路径，跳过
        if (distance > dist[node]) continue;
        
        // 遍历邻居节点
        if (graph.containsKey(node)) {
            for (int[] edge : graph.get(node)) {
                int neighbor = edge[0];
                int weight = edge[1];
                int newDist = dist[node] + weight;
                
                // 如果找到了更短的路径，更新距离并加入队列
                if (newDist < dist[neighbor]) {
                    dist[neighbor] = newDist;
                    pq.offer(new int[]{neighbor, newDist});
                }
            }
        }
    }
    
    return dist[end] == Integer.MAX_VALUE ? -1 : dist[end];
}
```

#### Bellman-Ford算法

##### 基本思想
适用于包含负权重边的图，能够检测负权重环。

##### 应用场景
1. 负权重图的最短路径
2. 负权重环检测

##### 经典例题
1. [便宜航班](https://leetcode.com/problems/cheapest-flights-within-k-stops/)
2. [网络延迟时间](https://leetcode.com/problems/network-delay-time/)（特殊情况）

##### 代码模板

```java
// Bellman-Ford算法模板
public int bellmanFord(int n, int[][] edges, int start, int end) {
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[start] = 0;
    
    // 进行n-1轮松弛操作
    for (int i = 0; i < n - 1; i++) {
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            
            if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    
    return dist[end] == Integer.MAX_VALUE ? -1 : dist[end];
}
```

#### Floyd-Warshall算法

##### 基本思想
解决所有顶点对之间的最短路径问题，基于动态规划思想。

##### 应用场景
1. 所有点对最短路径
2. 传递闭包
3. 最小环检测

##### 经典例题
1. [找到城市之间的最小代价](https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/)
2. [恰好移动k步到达目标的路径数](https://leetcode.com/problems/number-of-ways-to-arrive-at-destination/)

##### 代码模板

```java
// Floyd-Warshall算法模板
public int[][] floydWarshall(int n, int[][] edges) {
    int[][] dist = new int[n][n];
    
    // 初始化距离矩阵
    for (int i = 0; i < n; i++) {
        Arrays.fill(dist[i], Integer.MAX_VALUE);
        dist[i][i] = 0;
    }
    
    // 设置直接连接的边的权重
    for (int[] edge : edges) {
        int u = edge[0];
        int v = edge[1];
        int w = edge[2];
        dist[u][v] = Math.min(dist[u][v], w);
    }
    
    // Floyd-Warshall核心算法
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (dist[i][k] != Integer.MAX_VALUE && dist[k][j] != Integer.MAX_VALUE) {
                    dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
    }
    
    return dist;
}
```

### 3. 最小生成树算法

最小生成树是连通无向图的一个子图，它是一棵树，包含了图中的所有顶点，并且所有边的权重之和最小。

#### Prim算法

##### 基本思想
从任意顶点开始，每次选择连接已选顶点集合和未选顶点集合的最小权重边，逐步扩展生成树。

##### 应用场景
1. 网络设计
2. 电路设计
3. 聚类分析

##### 经典例题
1. [连接所有点的最小费用](https://leetcode.com/problems/min-cost-to-connect-all-points/)
2. [最优账单平衡](https://leetcode.com/problems/optimal-account-balancing/)

##### 代码模板

```java
// Prim算法模板
public int prim(int n, int[][] edges) {
    // 构建邻接表
    Map<Integer, List<int[]>> graph = new HashMap<>();
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        graph.computeIfAbsent(u, k -> new ArrayList<>()).add(new int[]{v, w});
        graph.computeIfAbsent(v, k -> new ArrayList<>()).add(new int[]{u, w});
    }
    
    // 记录已访问的顶点
    boolean[] visited = new boolean[n];
    // 优先队列，按权重排序
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
    
    // 从顶点0开始
    pq.offer(new int[]{0, 0});
    int cost = 0;
    int vertices = 0;
    
    while (!pq.isEmpty() && vertices < n) {
        int[] current = pq.poll();
        int node = current[0];
        int weight = current[1];
        
        if (visited[node]) continue;
        
        visited[node] = true;
        cost += weight;
        vertices++;
        
        // 添加相邻边到队列
        if (graph.containsKey(node)) {
            for (int[] edge : graph.get(node)) {
                int neighbor = edge[0];
                int edgeWeight = edge[1];
                if (!visited[neighbor]) {
                    pq.offer(new int[]{neighbor, edgeWeight});
                }
            }
        }
    }
    
    return vertices == n ? cost : -1;
}
```

#### Kruskal算法

##### 基本思想
将所有边按权重排序，依次选择不形成环的最小权重边，直到生成树包含n-1条边。

##### 应用场景
1. 网络设计
2. 图像分割
3. 聚类分析

##### 经典例题
1. [连接所有点的最小费用](https://leetcode.com/problems/min-cost-to-connect-all-points/)
2. [避免洪水泛滥](https://leetcode.com/problems/avoid-flood-in-the-city/)

##### 代码模板

```java
// 并查集类
class UnionFind {
    private int[] parent;
    private int[] rank;
    
    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }
    
    public int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]); // 路径压缩
        }
        return parent[x];
    }
    
    public boolean union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX == rootY) return false;
        
        // 按秩合并
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        
        return true;
    }
}

// Kruskal算法模板
public int kruskal(int n, int[][] edges) {
    // 按权重排序边
    Arrays.sort(edges, (a, b) -> a[2] - b[2]);
    
    UnionFind uf = new UnionFind(n);
    int cost = 0;
    int edgesUsed = 0;
    
    for (int[] edge : edges) {
        int u = edge[0], v = edge[1], w = edge[2];
        
        // 如果两个顶点不在同一连通分量中，则添加这条边
        if (uf.union(u, v)) {
            cost += w;
            edgesUsed++;
            
            // 如果已经添加了n-1条边，则生成树完成
            if (edgesUsed == n - 1) break;
        }
    }
    
    return edgesUsed == n - 1 ? cost : -1;
}
```

### 4. 拓扑排序

拓扑排序是对有向无环图(DAG)的顶点的一种线性排序，使得对于任何有向边(u,v)，顶点u在排序中都出现在顶点v之前。

#### 基本思想
通过不断移除入度为0的顶点来实现排序。

#### 应用场景
1. 任务调度
2. 课程安排
3. 依赖解析

#### 经典例题
1. [课程表](https://leetcode.com/problems/course-schedule/)
2. [课程表 II](https://leetcode.com/problems/course-schedule-ii/)
3. [项目管理](https://leetcode.com/problems/sort-items-by-groups-respecting-dependencies/)
4. [火星词典](https://leetcode.com/problems/alien-dictionary/)

#### 代码模板

```java
// 拓扑排序模板 - BFS(Kahn算法)
public int[] topologicalSortBFS(int n, int[][] prerequisites) {
    // 构建邻接表和入度数组
    List<List<Integer>> graph = new ArrayList<>();
    int[] indegree = new int[n];
    
    for (int i = 0; i < n; i++) {
        graph.add(new ArrayList<>());
    }
    
    for (int[] prereq : prerequisites) {
        graph.get(prereq[1]).add(prereq[0]);
        indegree[prereq[0]]++;
    }
    
    // 将入度为0的顶点加入队列
    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < n; i++) {
        if (indegree[i] == 0) {
            queue.offer(i);
        }
    }
    
    // 拓扑排序
    int[] result = new int[n];
    int index = 0;
    
    while (!queue.isEmpty()) {
        int node = queue.poll();
        result[index++] = node;
        
        // 更新邻居节点的入度
        for (int neighbor : graph.get(node)) {
            indegree[neighbor]--;
            if (indegree[neighbor] == 0) {
                queue.offer(neighbor);
            }
        }
    }
    
    // 如果所有顶点都被访问，则存在拓扑排序
    return index == n ? result : new int[0];
}

// 拓扑排序模板 - DFS
public int[] topologicalSortDFS(int n, int[][] prerequisites) {
    // 构建邻接表
    List<List<Integer>> graph = new ArrayList<>();
    for (int i = 0; i < n; i++) {
        graph.add(new ArrayList<>());
    }
    
    for (int[] prereq : prerequisites) {
        graph.get(prereq[1]).add(prereq[0]);
    }
    
    // 0: 未访问, 1: 正在访问, 2: 已完成访问
    int[] visited = new int[n];
    Stack<Integer> stack = new Stack<>();
    
    for (int i = 0; i < n; i++) {
        if (!dfs(graph, i, visited, stack)) {
            return new int[0]; // 存在环，无法进行拓扑排序
        }
    }
    
    // 构建结果数组
    int[] result = new int[n];
    for (int i = 0; i < n; i++) {
        result[i] = stack.pop();
    }
    
    return result;
}

private boolean dfs(List<List<Integer>> graph, int node, int[] visited, Stack<Integer> stack) {
    if (visited[node] == 1) return false; // 存在环
    if (visited[node] == 2) return true;  // 已经处理过
    
    visited[node] = 1; // 标记为正在访问
    
    for (int neighbor : graph.get(node)) {
        if (!dfs(graph, neighbor, visited, stack)) {
            return false;
        }
    }
    
    visited[node] = 2; // 标记为已完成访问
    stack.push(node);  // 将节点压入栈中
    return true;
}
```

### 5. 并查集(Union-Find)

并查集是一种树型的数据结构，用于处理一些不相交集合的合并及查询问题。

#### 基本思想
通过代表元来表示集合，支持高效的合并和查询操作。

#### 应用场景
1. 连通性检测
2. 最小生成树(Kruskal算法)
3. 动态连通性

#### 经典例题
1. [冗余连接](https://leetcode.com/problems/redundant-connection/)
2. [账户合并](https://leetcode.com/problems/accounts-merge/)
3. [情侣牵手](https://leetcode.com/problems/couples-holding-hands/)
4. [由斜杠划分区域](https://leetcode.com/problems/regions-cut-by-slashes/)

#### 代码模板

```java
// 并查集模板
class UnionFind {
    private int[] parent;
    private int[] rank;
    private int count; // 连通分量的数量
    
    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        count = n;
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }
    
    // 查找根节点（带路径压缩）
    public int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]); // 路径压缩
        }
        return parent[x];
    }
    
    // 合并两个集合（按秩合并）
    public boolean union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        
        if (rootX == rootY) return false; // 已经在同一集合中
        
        // 按秩合并
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        
        count--;
        return true;
    }
    
    // 判断两个元素是否在同一集合中
    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }
    
    // 返回连通分量的数量
    public int getCount() {
        return count;
    }
}

// 冗余连接
public int[] findRedundantConnection(int[][] edges) {
    UnionFind uf = new UnionFind(edges.length + 1);
    
    for (int[] edge : edges) {
        // 如果两个顶点已经在同一连通分量中，则这条边是冗余的
        if (!uf.union(edge[0], edge[1])) {
            return edge;
        }
    }
    
    return new int[0];
}
```

## 📚 总结

图论算法是解决复杂问题的强大工具，在LeetCode中有广泛的应用。掌握图论算法需要理解各种算法的思想和应用场景，并通过大量练习来提升解题能力。建议：

1. **熟练掌握图的表示方法和基本操作**
2. **深入理解各种图算法的原理和实现**
3. **掌握经典例题的解法**
4. **学会识别问题的图论特征**
5. **多做练习，积累经验**

通过系统学习图论算法，你将能够在面对复杂的LeetCode问题时游刃有余。