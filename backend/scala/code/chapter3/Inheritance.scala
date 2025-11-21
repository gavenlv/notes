object Inheritance {
  def main(args: Array[String]): Unit = {
    // 基本继承
    class Animal(val name: String, val age: Int) {
      def speak(): String = "Some sound"
      
      def eat(): Unit = println(s"$name is eating")
      
      override def toString: String = s"$name ($age years old)"
    }
    
    class Dog(name: String, age: Int, val breed: String) extends Animal(name, age) {
      override def speak(): String = "Woof! Woof!"
      
      def fetch(): Unit = println(s"$name is fetching the ball")
      
      override def toString: String = s"${super.toString} - $breed breed"
    }
    
    class Cat(name: String, age: Int, val isIndoor: Boolean) extends Animal(name, age) {
      override def speak(): String = "Meow!"
      
      def scratch(): Unit = println(s"$name is scratching")
      
      override def toString: String = s"${super.toString} - Indoor: $isIndoor"
    }
    
    val dog = new Dog("Buddy", 3, "Golden Retriever")
    val cat = new Cat("Whiskers", 5, true)
    
    println(dog)
    println(dog.speak())
    dog.fetch()
    dog.eat()
    
    println(cat)
    println(cat.speak())
    cat.scratch()
    cat.eat()
    
    // 调用父类构造器
    class Vehicle(val brand: String, val model: String, val year: Int) {
      def start(): Unit = println(s"$brand $model is starting")
      
      def stop(): Unit = println(s"$brand $model is stopping")
      
      override def toString: String = s"$year $brand $model"
    }
    
    class Car(brand: String, model: String, year: Int, 
              val numDoors: Int, val fuelType: String) 
         extends Vehicle(brand, model, year) {
      
      override def start(): Unit = {
        super.start()
        println(s"Engine running on $fuelType")
      }
      
      def honk(): Unit = println("Beep beep!")
      
      override def toString: String = s"${super.toString} - $numDoors doors, $fuelType"
    }
    
    val car = new Car("Toyota", "Corolla", 2020, 4, "gasoline")
    println(car)
    car.start()
    car.honk()
    
    // 类型检查与转换
    class Animal2
    class Dog2 extends Animal2
    class Cat2 extends Animal2
    class Bird2 extends Animal2
    
    val dog2 = new Dog2
    val cat2 = new Cat2
    val bird2 = new Bird2
    
    val animals: List[Animal2] = List(dog2, cat2, bird2)
    
    for (animal <- animals) {
      animal match {
        case d: Dog2 => println("Found a dog!")
        case c: Cat2 => println("Found a cat!")
        case b: Bird2 => println("Found a bird!")
      }
    }
    
    // 抽象类
    abstract class Shape {
      def area: Double
      def perimeter: Double
      
      def describe(): String = s"This shape has area $area and perimeter $perimeter"
      
      def draw(): Unit
    }
    
    class Circle(val radius: Double) extends Shape {
      def area: Double = Math.PI * radius * radius
      def perimeter: Double = 2 * Math.PI * radius
      
      def draw(): Unit = println(s"Drawing a circle with radius $radius")
      
      override def describe(): String = s"Circle - ${super.describe()}"
    }
    
    class Rectangle(val width: Double, val height: Double) extends Shape {
      def area: Double = width * height
      def perimeter: Double = 2 * (width + height)
      
      def draw(): Unit = println(s"Drawing a rectangle $width by $height")
      
      override def describe(): String = s"Rectangle - ${super.describe()}"
    }
    
    val shapes: List[Shape] = List(
      new Circle(5.0),
      new Rectangle(4.0, 6.0)
    )
    
    shapes.foreach { shape =>
      println(shape.describe())
      shape.draw()
    }
  }
}