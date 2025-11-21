object ClassesAndObjects {
  def main(args: Array[String]): Unit = {
    // 基本类定义和使用
    class Person {
      var name: String = "Unknown"
      var age: Int = 0
      
      def greet(): String = s"Hello, I'm $name and I'm $age years old"
      
      def celebrateBirthday(): Unit = {
        age += 1
        println(s"Happy birthday! Now I'm $age years old")
      }
    }
    
    val person = new Person()
    person.name = "Alice"
    person.age = 30
    println(person.greet())
    person.celebrateBirthday()
    
    // 带参数的类
    class Student(name: String, age: Int, major: String) {
      def introduce(): String = s"I'm $name, $age years old, studying $major"
      
      def study(hours: Int): String = s"$name is studying $major for $hours hours"
    }
    
    val student = new Student("Bob", 20, "Computer Science")
    println(student.introduce())
    println(student.study(3))
    
    // 使用val和var定义类参数
    class Employee(val id: Int, var name: String, var department: String) {
      def promote(newDepartment: String): Unit = {
        department = newDepartment
        println(s"$name has been promoted to $department")
      }
      
      override def toString: String = s"Employee(id=$id, name=$name, department=$department)"
    }
    
    val emp = new Employee(1001, "Carol", "Engineering")
    println(emp.id)
    emp.name = "Carol Smith"
    println(emp.name)
    emp.promote("Management")
    
    // 单例对象
    object MathUtils {
      val PI = 3.141592653589793
      
      def add(a: Int, b: Int): Int = a + b
      def multiply(a: Int, b: Int): Int = a * b
      def power(base: Int, exp: Int): Double = math.pow(base, exp)
    }
    
    println(s"PI value: ${MathUtils.PI}")
    println(s"5 + 3 = ${MathUtils.add(5, 3)}")
    println(s"5 * 3 = ${MathUtils.multiply(5, 3)}")
    println(s"2^10 = ${MathUtils.power(2, 10)}")
    
    // 伴生对象
    class BankAccount private(private var balance: Double) {
      def deposit(amount: Double): Unit = {
        if (amount > 0) balance += amount
      }
      
      def withdraw(amount: Double): Unit = {
        if (amount > 0 && amount <= balance) balance -= amount
      }
      
      def currentBalance: Double = balance
      
      override def toString: String = s"Balance: $$${balance}"
    }
    
    object BankAccount {
      def apply(initialBalance: Double): BankAccount = {
        new BankAccount(initialBalance)
      }
      
      def empty(): BankAccount = {
        new BankAccount(0.0)
      }
    }
    
    val account1 = BankAccount(1000.0)
    val account2 = BankAccount.empty()
    
    println(account1)
    println(account2)
    
    account1.deposit(200)
    account2.withdraw(100)
    println(account1)
    println(account2)
  }
}