// 在Java中调用Scala代码的示例

import scala.collection.JavaConverters;
import scala.collection.immutable.List;
import scala.Option;
import scala.Tuple2;

/**
 * 在Java中调用Scala代码的演示类
 */
public class JavaExample {
    public static void main(String[] args) {
        // 创建Scala类的实例
        ScalaClass scalaObj = new ScalaClass("Alice");
        
        // 调用Scala方法
        System.out.println("Name: " + scalaObj.getName());
        
        // 使用默认参数
        System.out.println("Greeting with default: " + scalaObj.greet());
        
        // 提供参数
        System.out.println("Greeting with custom: " + scalaObj.greet("Hi there"));
        
        // 修改状态
        scalaObj.setName("Bob");
        System.out.println("New name: " + scalaObj.getName());
        
        // 调用Scala对象的方法
        int sum = ScalaUtils.add(5, 3);
        int product = ScalaUtils.multiply(4, 7);
        System.out.println("Sum: " + sum + ", Product: " + product);
        
        // 调用返回Scala类型的方法
        // 1. 处理Scala List
        java.util.List<String> javaList = java.util.Arrays.asList("A", null, "B", null, "C");
        List<String> scalaList = JavaConverters.asScalaBuffer(javaList).toList();
        List<String> filteredList = scalaObj.processList(scalaList);
        
        // 转换回Java集合
        java.util.List<String> filteredJavaList = JavaConverters.seqAsJavaList(filteredList);
        System.out.println("Filtered list: " + filteredJavaList);
        
        // 2. 处理Option类型
        Option<String> found = scalaObj.findElement(scalaList, "B");
        if (found.isDefined()) {
            System.out.println("Found: " + found.get());
        } else {
            System.out.println("Not found");
        }
        
        // 3. 处理元组
        Tuple2<Integer, Integer> result = scalaObj.divideAndRemainder(17, 5);
        int quotient = result._1();
        int remainder = result._2();
        System.out.println("17 / 5 = " + quotient + " remainder " + remainder);
        
        // 使用Scala case class
        Person person = new Person("Charlie", 25);
        System.out.println("Person name: " + person.name());
        System.out.println("Person age: " + person.age());
        System.out.println("Is adult: " + person.isAdult());
        System.out.println(person.greet());
    }
}