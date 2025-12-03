import java.util.*;

/**
 * 第七章：图结构 - 复杂关系建模
 * 完整可运行的代码示例
 */
public class Chapter7Example {
    
    // 1. 邻接矩阵表示的图
    static class AdjacencyMatrixGraph {
        private int vertices;
        private boolean[][] adjMatrix;
        private boolean isDirected;
        
        public AdjacencyMatrixGraph(int vertices, boolean isDirected) {
            this.vertices = vertices;
            this.isDirected = isDirected;
            this.adjMatrix = new boolean[vertices][vertices];
        }
        
        public void addEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                adjMatrix[src][dest] = true;
                if (!isDirected) {
                    adjMatrix[dest][src] = true;
                }
                System.out.println("邻接矩阵 - 添加边: " + src + " -> " + dest);
            }
        }
        
        public void removeEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                adjMatrix[src][dest] = false;
                if (!isDirected) {
                    adjMatrix[dest][src] = false;
                }
                System.out.println("邻接矩阵 - 删除边: " + src + " -> " + dest);
            }
        }
        
        public boolean hasEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                return adjMatrix[src][dest];
            }
            return false;
        }
        
        public List<Integer> getNeighbors(int vertex) {
            List<Integer> neighbors = new ArrayList<>();
            if (vertex >= 0 && vertex < vertices) {
                for (int i = 0; i < vertices; i++) {
                    if (adjMatrix[vertex][i]) {
                        neighbors.add(i);
                    }
                }
            }
            return neighbors;
        }
        
        public int getDegree(int vertex) {
            int degree = 0;
            if (vertex >= 0 && vertex < vertices) {
                for (int i = 0; i < vertices; i++) {
                    if (adjMatrix[vertex][i]) {
                        degree++;
                    }
                }
            }
            return degree;
        }
        
        public void printGraph() {
            System.out.println("邻接矩阵表示的图:");
            System.out.print("   ");
            for (int i = 0; i < vertices; i++) {
                System.out.printf("%3d", i);
            }
            System.out.println();
            
            for (int i = 0; i < vertices; i++) {
                System.out.printf("%2d:", i);
                for (int j = 0; j < vertices; j++) {
                    System.out.printf("%3s", adjMatrix[i][j] ? "1" : "0");
                }
                System.out.println();
            }
        }
    }
    
    // 2. 邻接表表示的图
    static class AdjacencyListGraph {
        private int vertices;
        private List<List<Integer>> adjList;
        private boolean isDirected;
        
        public AdjacencyListGraph(int vertices, boolean isDirected) {
            this.vertices = vertices;
            this.isDirected = isDirected;
            this.adjList = new ArrayList<>(vertices);
            
            for (int i = 0; i < vertices; i++) {
                adjList.add(new ArrayList<>());
            }
        }
        
        public void addEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                adjList.get(src).add(dest);
                if (!isDirected) {
                    adjList.get(dest).add(src);
                }
                System.out.println("邻接表 - 添加边: " + src + " -> " + dest);
            }
        }
        
        public void removeEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                adjList.get(src).remove(Integer.valueOf(dest));
                if (!isDirected) {
                    adjList.get(dest).remove(Integer.valueOf(src));
                }
                System.out.println("邻接表 - 删除边: " + src + " -> " + dest);
            }
        }
        
        public boolean hasEdge(int src, int dest) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                return adjList.get(src).contains(dest);
            }
            return false;
        }
        
        public List<Integer> getNeighbors(int vertex) {
            if (vertex >= 0 && vertex < vertices) {
                return new ArrayList<>(adjList.get(vertex));
            }
            return new ArrayList<>();
        }
        
        public int getDegree(int vertex) {
            if (vertex >= 0 && vertex < vertices) {
                return adjList.get(vertex).size();
            }
            return 0;
        }
        
        public void printGraph() {
            System.out.println("邻接表表示的图:");
            for (int i = 0; i < vertices; i++) {
                System.out.print(i + ": ");
                for (int neighbor : adjList.get(i)) {
                    System.out.print(neighbor + " ");
                }
                System.out.println();
            }
        }
    }
    
    // 3. 边的表示
    static class Edge {
        int src;
        int dest;
        int weight;
        
        public Edge(int src, int dest, int weight) {
            this.src = src;
            this.dest = dest;
            this.weight = weight;
        }
        
        @Override
        public String toString() {
            return "(" + src + "->" + dest + ", " + weight + ")";
        }
    }
    
    // 4. 边的列表表示的图
    static class EdgeListGraph {
        private int vertices;
        private List<Edge> edgeList;
        private boolean isDirected;
        private boolean isWeighted;
        
        public EdgeListGraph(int vertices, boolean isDirected, boolean isWeighted) {
            this.vertices = vertices;
            this.isDirected = isDirected;
            this.isWeighted = isWeighted;
            this.edgeList = new ArrayList<>();
        }
        
        public void addEdge(int src, int dest, int weight) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                edgeList.add(new Edge(src, dest, weight));
                if (!isDirected) {
                    edgeList.add(new Edge(dest, src, weight));
                }
                System.out.println("边列表 - 添加边: (" + src + "->" + dest + ", " + weight + ")");
            }
        }
        
        public void addEdge(int src, int dest) {
            addEdge(src, dest, 1);
        }
        
        public List<Edge> getEdges() {
            return new ArrayList<>(edgeList);
        }
        
        public List<Integer> getNeighbors(int vertex) {
            List<Integer> neighbors = new ArrayList<>();
            for (Edge edge : edgeList) {
                if (edge.src == vertex) {
                    neighbors.add(edge.dest);
                }
            }
            return neighbors;
        }
        
        public void printGraph() {
            System.out.println("边列表表示的图:");
            for (Edge edge : edgeList) {
                System.out.println(edge);
            }
        }
    }
    
    // 5. DFS图遍历
    static class DFSGraph extends AdjacencyListGraph {
        
        public DFSGraph(int vertices, boolean isDirected) {
            super(vertices, isDirected);
        }
        
        public void dfsRecursive(int startVertex) {
            boolean[] visited = new boolean[super.vertices];
            System.out.print("DFS遍历 (递归): ");
            dfsRecursiveHelper(startVertex, visited);
            System.out.println();
        }
        
        private void dfsRecursiveHelper(int vertex, boolean[] visited) {
            visited[vertex] = true;
            System.out.print(vertex + " ");
            
            for (int neighbor : super.getNeighbors(vertex)) {
                if (!visited[neighbor]) {
                    dfsRecursiveHelper(neighbor, visited);
                }
            }
        }
        
        public void dfsIterative(int startVertex) {
            boolean[] visited = new boolean[super.vertices];
            Stack<Integer> stack = new Stack<>();
            
            stack.push(startVertex);
            System.out.print("DFS遍历 (迭代): ");
            
            while (!stack.isEmpty()) {
                int vertex = stack.pop();
                
                if (!visited[vertex]) {
                    visited[vertex] = true;
                    System.out.print(vertex + " ");
                    
                    List<Integer> neighbors = super.getNeighbors(vertex);
                    for (int i = neighbors.size() - 1; i >= 0; i--) {
                        int neighbor = neighbors.get(i);
                        if (!visited[neighbor]) {
                            stack.push(neighbor);
                        }
                    }
                }
            }
            System.out.println();
        }
    }
    
    // 6. BFS图遍历
    static class BFSGraph extends AdjacencyListGraph {
        
        public BFSGraph(int vertices, boolean isDirected) {
            super(vertices, isDirected);
        }
        
        public void bfs(int startVertex) {
            boolean[] visited = new boolean[super.vertices];
            Queue<Integer> queue = new LinkedList<>();
            
            visited[startVertex] = true;
            queue.offer(startVertex);
            System.out.print("BFS遍历: ");
            
            while (!queue.isEmpty()) {
                int vertex = queue.poll();
                System.out.print(vertex + " ");
                
                for (int neighbor : super.getNeighbors(vertex)) {
                    if (!visited[neighbor]) {
                        visited[neighbor] = true;
                        queue.offer(neighbor);
                    }
                }
            }
            System.out.println();
        }
        
        public List<Integer> findShortestPath(int src, int dest) {
            if (src == dest) {
                return Arrays.asList(src);
            }
            
            boolean[] visited = new boolean[super.vertices];
            int[] parent = new int[super.vertices];
            Queue<Integer> queue = new LinkedList<>();
            
            for (int i = 0; i < super.vertices; i++) {
                parent[i] = -1;
            }
            
            visited[src] = true;
            queue.offer(src);
            
            while (!queue.isEmpty()) {
                int vertex = queue.poll();
                
                if (vertex == dest) {
                    return reconstructPath(parent, src, dest);
                }
                
                for (int neighbor : super.getNeighbors(vertex)) {
                    if (!visited[neighbor]) {
                        visited[neighbor] = true;
                        parent[neighbor] = vertex;
                        queue.offer(neighbor);
                    }
                }
            }
            
            return new ArrayList<>();
        }
        
        private List<Integer> reconstructPath(int[] parent, int src, int dest) {
            List<Integer> path = new ArrayList<>();
            int current = dest;
            
            while (current != -1) {
                path.add(current);
                current = parent[current];
            }
            
            Collections.reverse(path);
            return path;
        }
    }
    
    // 7. Dijkstra算法
    static class DijkstraGraph extends AdjacencyListGraph {
        static class WeightedEdge {
            int dest;
            int weight;
            
            public WeightedEdge(int dest, int weight) {
                this.dest = dest;
                this.weight = weight;
            }
        }
        
        private List<List<WeightedEdge>> weightedAdjList;
        
        public DijkstraGraph(int vertices) {
            super(vertices, true);
            this.weightedAdjList = new ArrayList<>(vertices);
            for (int i = 0; i < vertices; i++) {
                weightedAdjList.add(new ArrayList<>());
            }
        }
        
        public void addWeightedEdge(int src, int dest, int weight) {
            if (src >= 0 && src < super.vertices && dest >= 0 && dest < super.vertices) {
                weightedAdjList.get(src).add(new WeightedEdge(dest, weight));
                System.out.println("Dijkstra - 添加带权重边: " + src + " -> " + dest + " (权重: " + weight + ")");
            }
        }
        
        public int[] dijkstra(int src) {
            int[] dist = new int[super.vertices];
            boolean[] visited = new boolean[super.vertices];
            
            Arrays.fill(dist, Integer.MAX_VALUE);
            dist[src] = 0;
            
            PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
            pq.offer(new int[]{src, 0});
            
            System.out.println("Dijkstra算法执行过程:");
            
            while (!pq.isEmpty()) {
                int[] current = pq.poll();
                int u = current[0];
                int distance = current[1];
                
                if (visited[u]) continue;
                
                visited[u] = true;
                System.out.println("  访问顶点 " + u + "，当前距离: " + distance);
                
                for (WeightedEdge edge : weightedAdjList.get(u)) {
                    int v = edge.dest;
                    int weight = edge.weight;
                    
                    if (!visited[v] && dist[u] != Integer.MAX_VALUE && dist[u] + weight < dist[v]) {
                        dist[v] = dist[u] + weight;
                        pq.offer(new int[]{v, dist[v]});
                        System.out.println("    更新顶点 " + v + " 的距离为: " + dist[v]);
                    }
                }
            }
            
            return dist;
        }
        
        public void printShortestDistances(int src, int[] distances) {
            System.out.println("从顶点 " + src + " 到各顶点的最短距离:");
            for (int i = 0; i < distances.length; i++) {
                if (distances[i] == Integer.MAX_VALUE) {
                    System.out.println("  到顶点 " + i + ": 无法到达");
                } else {
                    System.out.println("  到顶点 " + i + ": " + distances[i]);
                }
            }
        }
    }
    
    // 8. Floyd-Warshall算法
    static class FloydWarshallGraph {
        private int vertices;
        private int[][] graph;
        private static final int INF = Integer.MAX_VALUE;
        
        public FloydWarshallGraph(int vertices) {
            this.vertices = vertices;
            this.graph = new int[vertices][vertices];
            
            for (int i = 0; i < vertices; i++) {
                for (int j = 0; j < vertices; j++) {
                    if (i == j) {
                        graph[i][j] = 0;
                    } else {
                        graph[i][j] = INF;
                    }
                }
            }
        }
        
        public void addEdge(int src, int dest, int weight) {
            if (src >= 0 && src < vertices && dest >= 0 && dest < vertices) {
                graph[src][dest] = weight;
                System.out.println("Floyd-Warshall - 添加带权重边: " + src + " -> " + dest + " (权重: " + weight + ")");
            }
        }
        
        public int[][] floydWarshall() {
            int[][] dist = new int[vertices][vertices];
            for (int i = 0; i < vertices; i++) {
                for (int j = 0; j < vertices; j++) {
                    dist[i][j] = graph[i][j];
                }
            }
            
            System.out.println("Floyd-Warshall算法执行过程:");
            
            for (int k = 0; k < vertices; k++) {
                System.out.println("  以顶点 " + k + " 作为中间顶点:");
                
                for (int i = 0; i < vertices; i++) {
                    for (int j = 0; j < vertices; j++) {
                        if (dist[i][k] != INF && dist[k][j] != INF) {
                            if (dist[i][k] + dist[k][j] < dist[i][j]) {
                                dist[i][j] = dist[i][k] + dist[k][j];
                                System.out.println("    更新路径: " + i + " -> " + j + 
                                                 " (通过 " + k + ")，新距离: " + dist[i][j]);
                            }
                        }
                    }
                }
            }
            
            return dist;
        }
        
        public void printDistanceMatrix(int[][] dist) {
            System.out.println("所有顶点对之间的最短距离矩阵:");
            System.out.printf("%4s", "");
            for (int i = 0; i < vertices; i++) {
                System.out.printf("%6d", i);
            }
            System.out.println();
            
            for (int i = 0; i < vertices; i++) {
                System.out.printf("%3d:", i);
                for (int j = 0; j < vertices; j++) {
                    if (dist[i][j] == INF) {
                        System.out.printf("%6s", "INF");
                    } else {
                        System.out.printf("%6d", dist[i][j]);
                    }
                }
                System.out.println();
            }
        }
    }
    
    // 9. Kruskal算法
    static class KruskalMST {
        static class Edge implements Comparable<Edge> {
            int src, dest, weight;
            
            public Edge(int src, int dest, int weight) {
                this.src = src;
                this.dest = dest;
                this.weight = weight;
            }
            
            @Override
            public int compareTo(Edge other) {
                return this.weight - other.weight;
            }
        }
        
        static class UnionFind {
            private int[] parent;
            private int[] rank;
            
            public UnionFind(int n) {
                parent = new int[n];
                rank = new int[n];
                for (int i = 0; i < n; i++) {
                    parent[i] = i;
                    rank[i] = 0;
                }
            }
            
            public int find(int x) {
                if (parent[x] != x) {
                    parent[x] = find(parent[x]);
                }
                return parent[x];
            }
            
            public void union(int x, int y) {
                int rootX = find(x);
                int rootY = find(y);
                
                if (rootX != rootY) {
                    if (rank[rootX] < rank[rootY]) {
                        parent[rootX] = rootY;
                    } else if (rank[rootX] > rank[rootY]) {
                        parent[rootY] = rootX;
                    } else {
                        parent[rootY] = rootX;
                        rank[rootX]++;
                    }
                }
            }
        }
        
        private int vertices;
        private List<Edge> edges;
        
        public KruskalMST(int vertices) {
            this.vertices = vertices;
            this.edges = new ArrayList<>();
        }
        
        public void addEdge(int src, int dest, int weight) {
            edges.add(new Edge(src, dest, weight));
            System.out.println("Kruskal - 添加边: (" + src + ", " + dest + ", " + weight + ")");
        }
        
        public List<Edge> kruskalMST() {
            List<Edge> result = new ArrayList<>();
            
            Collections.sort(edges);
            System.out.println("按权重排序后的边:");
            for (Edge edge : edges) {
                System.out.println("  (" + edge.src + ", " + edge.dest + ", " + edge.weight + ")");
            }
            
            UnionFind uf = new UnionFind(vertices);
            
            System.out.println("Kruskal算法执行过程:");
            
            for (Edge edge : edges) {
                int rootSrc = uf.find(edge.src);
                int rootDest = uf.find(edge.dest);
                
                if (rootSrc != rootDest) {
                    result.add(edge);
                    uf.union(rootSrc, rootDest);
                    System.out.println("  选择边: (" + edge.src + ", " + edge.dest + ", " + edge.weight + ")");
                } else {
                    System.out.println("  跳过边: (" + edge.src + ", " + edge.dest + ", " + edge.weight + ") (会形成环)");
                }
                
                if (result.size() == vertices - 1) {
                    break;
                }
            }
            
            return result;
        }
        
        public void printMST(List<Edge> mst) {
            System.out.println("最小生成树的边:");
            int totalWeight = 0;
            for (Edge edge : mst) {
                System.out.println("  (" + edge.src + ", " + edge.dest + ", " + edge.weight + ")");
                totalWeight += edge.weight;
            }
            System.out.println("最小生成树的总权重: " + totalWeight);
        }
    }
    
    // 10. Prim算法
    static class PrimMST extends AdjacencyListGraph {
        static class WeightedEdge {
            int dest;
            int weight;
            
            public WeightedEdge(int dest, int weight) {
                this.dest = dest;
                this.weight = weight;
            }
        }
        
        private List<List<WeightedEdge>> weightedAdjList;
        
        public PrimMST(int vertices) {
            super(vertices, false);
            this.weightedAdjList = new ArrayList<>(vertices);
            for (int i = 0; i < vertices; i++) {
                weightedAdjList.add(new ArrayList<>());
            }
        }
        
        public void addWeightedEdge(int src, int dest, int weight) {
            if (src >= 0 && src < super.vertices && dest >= 0 && dest < super.vertices) {
                weightedAdjList.get(src).add(new WeightedEdge(dest, weight));
                weightedAdjList.get(dest).add(new WeightedEdge(src, weight));
                System.out.println("Prim - 添加带权重边: " + src + " <-> " + dest + " (权重: " + weight + ")");
            }
        }
        
        public List<Edge> primMST() {
            List<Edge> result = new ArrayList<>();
            boolean[] inMST = new boolean[super.vertices];
            int[] minEdge = new int[super.vertices];
            int[] parent = new int[super.vertices];
            
            Arrays.fill(minEdge, Integer.MAX_VALUE);
            Arrays.fill(parent, -1);
            
            minEdge[0] = 0;
            
            System.out.println("Prim算法执行过程:");
            
            for (int count = 0; count < super.vertices - 1; count++) {
                int u = findMinVertex(minEdge, inMST);
                inMST[u] = true;
                
                System.out.println("  选择顶点: " + u);
                
                for (WeightedEdge edge : weightedAdjList.get(u)) {
                    int v = edge.dest;
                    int weight = edge.weight;
                    
                    if (!inMST[v] && weight < minEdge[v]) {
                        minEdge[v] = weight;
                        parent[v] = u;
                        System.out.println("    更新顶点 " + v + " 的最小边权重为: " + weight);
                    }
                }
            }
            
            for (int i = 1; i < super.vertices; i++) {
                if (parent[i] != -1) {
                    result.add(new Edge(parent[i], i, minEdge[i]));
                }
            }
            
            return result;
        }
        
        private int findMinVertex(int[] minEdge, boolean[] inMST) {
            int min = Integer.MAX_VALUE;
            int minIndex = -1;
            
            for (int v = 0; v < super.vertices; v++) {
                if (!inMST[v] && minEdge[v] < min) {
                    min = minEdge[v];
                    minIndex = v;
                }
            }
            
            return minIndex;
        }
        
        public void printMST(List<Edge> mst) {
            System.out.println("Prim算法生成的最小生成树:");
            int totalWeight = 0;
            for (Edge edge : mst) {
                System.out.println("  (" + edge.src + ", " + edge.dest + ", " + edge.weight + ")");
                totalWeight += edge.weight;
            }
            System.out.println("最小生成树的总权重: " + totalWeight);
        }
    }
    
    // 11. 拓扑排序
    static class TopologicalSort extends AdjacencyListGraph {
        
        public TopologicalSort(int vertices) {
            super(vertices, true);
        }
        
        public List<Integer> topologicalSortDFS() {
            boolean[] visited = new boolean[super.vertices];
            Stack<Integer> stack = new Stack<>();
            
            System.out.println("拓扑排序 (DFS方法) 执行过程:");
            
            for (int i = 0; i < super.vertices; i++) {
                if (!visited[i]) {
                    dfsForTopoSort(i, visited, stack);
                }
            }
            
            List<Integer> result = new ArrayList<>();
            while (!stack.isEmpty()) {
                result.add(stack.pop());
            }
            
            return result;
        }
        
        private void dfsForTopoSort(int vertex, boolean[] visited, Stack<Integer> stack) {
            visited[vertex] = true;
            System.out.println("  访问顶点: " + vertex);
            
            for (int neighbor : super.getNeighbors(vertex)) {
                if (!visited[neighbor]) {
                    dfsForTopoSort(neighbor, visited, stack);
                }
            }
            
            stack.push(vertex);
            System.out.println("  顶点 " + vertex + " 处理完毕，入栈");
        }
        
        public List<Integer> topologicalSortKahn() {
            int[] inDegree = new int[super.vertices];
            for (int i = 0; i < super.vertices; i++) {
                for (int neighbor : super.getNeighbors(i)) {
                    inDegree[neighbor]++;
                }
            }
            
            System.out.println("拓扑排序 (Kahn算法) 执行过程:");
            System.out.print("  各顶点的入度: ");
            for (int i = 0; i < super.vertices; i++) {
                System.out.print(i + ":" + inDegree[i] + " ");
            }
            System.out.println();
            
            Queue<Integer> queue = new LinkedList<>();
            for (int i = 0; i < super.vertices; i++) {
                if (inDegree[i] == 0) {
                    queue.offer(i);
                    System.out.println("  将入度为0的顶点 " + i + " 加入队列");
                }
            }
            
            List<Integer> result = new ArrayList<>();
            
            while (!queue.isEmpty()) {
                int vertex = queue.poll();
                result.add(vertex);
                System.out.println("  处理顶点: " + vertex);
                
                for (int neighbor : super.getNeighbors(vertex)) {
                    inDegree[neighbor]--;
                    System.out.println("    顶点 " + neighbor + " 的入度减1，当前入度: " + inDegree[neighbor]);
                    
                    if (inDegree[neighbor] == 0) {
                        queue.offer(neighbor);
                        System.out.println("    将入度为0的顶点 " + neighbor + " 加入队列");
                    }
                }
            }
            
            if (result.size() != super.vertices) {
                System.out.println("图中存在环，无法进行拓扑排序");
                return new ArrayList<>();
            }
            
            return result;
        }
    }
    
    // 主测试方法
    public static void main(String[] args) {
        System.out.println("=== 第七章：图结构 - 复杂关系建模 ===\n");
        
        // 1. 测试邻接矩阵
        System.out.println("1. 邻接矩阵表示测试:");
        AdjacencyMatrixGraph matrixGraph = new AdjacencyMatrixGraph(5, false);
        matrixGraph.addEdge(0, 1);
        matrixGraph.addEdge(0, 4);
        matrixGraph.addEdge(1, 2);
        matrixGraph.addEdge(1, 3);
        matrixGraph.addEdge(1, 4);
        matrixGraph.addEdge(2, 3);
        matrixGraph.addEdge(3, 4);
        matrixGraph.printGraph();
        System.out.println("顶点1的度: " + matrixGraph.getDegree(1));
        System.out.println("是否存在边(1,3): " + matrixGraph.hasEdge(1, 3));
        System.out.println();
        
        // 2. 测试邻接表
        System.out.println("2. 邻接表表示测试:");
        AdjacencyListGraph listGraph = new AdjacencyListGraph(5, false);
        listGraph.addEdge(0, 1);
        listGraph.addEdge(0, 4);
        listGraph.addEdge(1, 2);
        listGraph.addEdge(1, 3);
        listGraph.addEdge(1, 4);
        listGraph.addEdge(2, 3);
        listGraph.addEdge(3, 4);
        listGraph.printGraph();
        System.out.println("顶点1的度: " + listGraph.getDegree(1));
        System.out.println("顶点1的邻居: " + listGraph.getNeighbors(1));
        System.out.println();
        
        // 3. 测试DFS遍历
        System.out.println("3. DFS遍历测试:");
        DFSGraph dfsGraph = new DFSGraph(5, false);
        dfsGraph.addEdge(0, 1);
        dfsGraph.addEdge(0, 4);
        dfsGraph.addEdge(1, 2);
        dfsGraph.addEdge(1, 3);
        dfsGraph.addEdge(1, 4);
        dfsGraph.addEdge(2, 3);
        dfsGraph.addEdge(3, 4);
        dfsGraph.dfsRecursive(0);
        dfsGraph.dfsIterative(0);
        System.out.println();
        
        // 4. 测试BFS遍历
        System.out.println("4. BFS遍历测试:");
        BFSGraph bfsGraph = new BFSGraph(5, false);
        bfsGraph.addEdge(0, 1);
        bfsGraph.addEdge(0, 4);
        bfsGraph.addEdge(1, 2);
        bfsGraph.addEdge(1, 3);
        bfsGraph.addEdge(1, 4);
        bfsGraph.addEdge(2, 3);
        bfsGraph.addEdge(3, 4);
        bfsGraph.bfs(0);
        System.out.println("从0到3的最短路径: " + bfsGraph.findShortestPath(0, 3));
        System.out.println();
        
        // 5. 测试Dijkstra算法
        System.out.println("5. Dijkstra算法测试:");
        DijkstraGraph dijkstraGraph = new DijkstraGraph(5);
        dijkstraGraph.addWeightedEdge(0, 1, 10);
        dijkstraGraph.addWeightedEdge(0, 4, 5);
        dijkstraGraph.addWeightedEdge(1, 2, 1);
        dijkstraGraph.addWeightedEdge(1, 4, 2);
        dijkstraGraph.addWeightedEdge(2, 3, 4);
        dijkstraGraph.addWeightedEdge(3, 2, 6);
        dijkstraGraph.addWeightedEdge(4, 1, 3);
        dijkstraGraph.addWeightedEdge(4, 2, 9);
        dijkstraGraph.addWeightedEdge(4, 3, 2);
        int[] distances = dijkstraGraph.dijkstra(0);
        dijkstraGraph.printShortestDistances(0, distances);
        System.out.println();
        
        // 6. 测试Floyd-Warshall算法
        System.out.println("6. Floyd-Warshall算法测试:");
        FloydWarshallGraph fwGraph = new FloydWarshallGraph(4);
        fwGraph.addEdge(0, 1, 5);
        fwGraph.addEdge(0, 3, 10);
        fwGraph.addEdge(1, 2, 3);
        fwGraph.addEdge(2, 3, 1);
        int[][] distMatrix = fwGraph.floydWarshall();
        fwGraph.printDistanceMatrix(distMatrix);
        System.out.println();
        
        // 7. 测试Kruskal算法
        System.out.println("7. Kruskal算法测试:");
        KruskalMST kruskalMST = new KruskalMST(4);
        kruskalMST.addEdge(0, 1, 10);
        kruskalMST.addEdge(0, 2, 6);
        kruskalMST.addEdge(0, 3, 5);
        kruskalMST.addEdge(1, 3, 15);
        kruskalMST.addEdge(2, 3, 4);
        List<KruskalMST.Edge> mstEdges = kruskalMST.kruskalMST();
        kruskalMST.printMST(mstEdges);
        System.out.println();
        
        // 8. 测试Prim算法
        System.out.println("8. Prim算法测试:");
        PrimMST primMST = new PrimMST(4);
        primMST.addWeightedEdge(0, 1, 10);
        primMST.addWeightedEdge(0, 2, 6);
        primMST.addWeightedEdge(0, 3, 5);
        primMST.addWeightedEdge(1, 3, 15);
        primMST.addWeightedEdge(2, 3, 4);
        List<Edge> primEdges = primMST.primMST();
        primMST.printMST(primEdges);
        System.out.println();
        
        // 9. 测试拓扑排序
        System.out.println("9. 拓扑排序测试:");
        TopologicalSort topoGraph = new TopologicalSort(6);
        topoGraph.addEdge(5, 2);
        topoGraph.addEdge(5, 0);
        topoGraph.addEdge(4, 0);
        topoGraph.addEdge(4, 1);
        topoGraph.addEdge(2, 3);
        topoGraph.addEdge(3, 1);
        System.out.println("DFS方法拓扑排序结果: " + topoGraph.topologicalSortDFS());
        System.out.println("Kahn算法拓扑排序结果: " + topoGraph.topologicalSortKahn());
    }
}