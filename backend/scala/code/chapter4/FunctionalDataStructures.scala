object FunctionalDataStructures {
  def main(args: Array[String]): Unit = {
    // 不可变集合
    val list1 = List(1, 2, 3)
    val list2 = 0 :: list1
    val list3 = list1 :+ 4
    
    println(s"list1: $list1")
    println(s"list2: $list2")
    println(s"list3: $list3")
    
    // 自定义不可变链表
    sealed trait MyList[+A]
    case object MyNil extends MyList[Nothing]
    case class MyCons[+A](head: A, tail: MyList[A]) extends MyList[A]
    
    object MyList {
      def apply[A](as: A*): MyList[A] = {
        if (as.isEmpty) MyNil
        else MyCons(as.head, apply(as.tail: _*))
      }
      
      def sum(ints: MyList[Int]): Int = ints match {
        case MyNil => 0
        case MyCons(h, t) => h + sum(t)
      }
      
      def map[A, B](l: MyList[A])(f: A => B): MyList[B] = {
        def loop(remaining: MyList[A], acc: MyList[B]): MyList[B] = remaining match {
          case MyNil => acc.reverse
          case MyCons(h, t) => loop(t, MyCons(f(h), acc))
        }
        loop(l, MyNil)
      }
      
      def filter[A](l: MyList[A])(f: A => Boolean): MyList[A] = {
        def loop(remaining: MyList[A], acc: MyList[A]): MyList[A] = remaining match {
          case MyNil => acc.reverse
          case MyCons(h, t) => 
            if (f(h)) loop(t, MyCons(h, acc))
            else loop(t, acc)
        }
        loop(l, MyNil)
      }
    }
    
    val myList = MyList(1, 2, 3, 4, 5)
    println(s"MyList sum: ${MyList.sum(myList)}")
    println(s"MyList map (*2): ${MyList.map(myList)(_ * 2)}")
    println(s"MyList filter (even): ${MyList.filter(myList)(_ % 2 == 0)}")
    
    // 二叉树
    sealed trait Tree[+A]
    case class Leaf[A](value: A) extends Tree[A]
    case class Branch[A](left: Tree[A], right: Tree[A]) extends Tree[A]
    
    object Tree {
      def size[A](t: Tree[A]): Int = t match {
        case Leaf(_) => 1
        case Branch(l, r) => 1 + size(l) + size(r)
      }
      
      def maximum(t: Tree[Int]): Int = t match {
        case Leaf(v) => v
        case Branch(l, r) => maximum(l).max(maximum(r))
      }
      
      def depth[A](t: Tree[A]): Int = t match {
        case Leaf(_) => 0
        case Branch(l, r) => 1 + (depth(l).max(depth(r)))
      }
      
      def map[A, B](t: Tree[A])(f: A => B): Tree[B] = t match {
        case Leaf(v) => Leaf(f(v))
        case Branch(l, r) => Branch(map(l)(f), map(r)(f))
      }
    }
    
    val tree = Branch(
      Branch(Leaf(1), Leaf(2)),
      Branch(Leaf(3), Branch(Leaf(4), Leaf(5)))
    )
    
    println(s"Tree size: ${Tree.size(tree)}")
    println(s"Tree maximum: ${Tree.maximum(tree)}")
    println(s"Tree depth: ${Tree.depth(tree)}")
    println(s"Tree map (*2): ${Tree.map(tree)(_ * 2)}")
    
    // 函数式设计模式：记忆化
    def memoize[A, B](f: A => B): A => B = {
      val cache = scala.collection.mutable.Map[A, B]()
      
      (a: A) => {
        if (cache.contains(a)) {
          cache(a)
        } else {
          val result = f(a)
          cache(a) = result
          result
        }
      }
    }
    
    def fibonacci(n: Int): BigInt = {
      if (n <= 1) n
      else fibonacci(n - 1) + fibonacci(n - 2)
    }
    
    val memoizedFib = memoize(fibonacci)
    println(s"memoizedFib(10): ${memoizedFib(10)}")
    println(s"memoizedFib(10) again: ${memoizedFib(10)}") // 从缓存获取
  }
}