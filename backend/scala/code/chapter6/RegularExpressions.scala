import scala.util.matching.Regex

object RegularExpressions {
  def main(args: Array[String]): Unit = {
    // 基本正则表达式
    val emailPattern = """.+@.+\..+""".r
    val phonePattern = """\d{3}-\d{3}-\d{4}""".r
    val zipCodePattern = """\d{5}(-\d{4})?""".r
    
    // 测试字符串匹配
    val email1 = "user@example.com"
    val email2 = "invalid.email"
    val phone1 = "123-456-7890"
    val phone2 = "12-3456-7890"
    val zip1 = "12345"
    val zip2 = "12345-6789"
    val zip3 = "1234"
    
    println(s"$email1 matches email pattern: ${emailPattern.pattern.matcher(email1).matches()}")
    println(s"$email2 matches email pattern: ${emailPattern.pattern.matcher(email2).matches()}")
    println(s"$phone1 matches phone pattern: ${phonePattern.pattern.matcher(phone1).matches()}")
    println(s"$phone2 matches phone pattern: ${phonePattern.pattern.matcher(phone2).matches()}")
    println(s"$zip1 matches zip pattern: ${zipCodePattern.pattern.matcher(zip1).matches()}")
    println(s"$zip2 matches zip pattern: ${zipCodePattern.pattern.matcher(zip2).matches()}")
    println(s"$zip3 matches zip pattern: ${zipCodePattern.pattern.matcher(zip3).matches()}")
    
    // 使用findFirstIn
    val text = "Contact us at support@example.com or sales@example.org"
    val emails = emailPattern.findAllIn(text).toList
    println(s"Found emails: $emails")  // Found emails: List(support@example.com, sales@example.org)
    
    // 使用findFirstMatchIn
    val firstEmail = emailPattern.findFirstMatchIn(text)
    println(s"First email: ${firstEmail.map(_.matched)}")  // First email: Some(support@example.com)
    
    // 提取匹配组
    val detailedEmailPattern = """([^@]+)@([^.]+)\.([^.]*)""".r
    
    def parseEmail(email: String): Option[(String, String, String)] = {
      detailedEmailPattern.findFirstMatchIn(email).map { m =>
        (m.group(1), m.group(2), m.group(3))
      }
    }
    
    println(parseEmail("user@example.com"))  // Some((user,example,com))
    println(parseEmail("invalid.email"))      // None
    
    // 正则表达式在模式匹配中的应用
    val datePattern = """(\d{4})-(\d{2})-(\d{2})""".r
    
    def formatDate(dateStr: String): String = dateStr match {
      case datePattern(year, month, day) => 
        f"$day/$month/$year"
      case _ => 
        s"Invalid date format: $dateStr"
    }
    
    println(formatDate("2023-12-25"))  // 25/12/2023
    println(formatDate("25-12-2023"))  // Invalid date format: 25-12-2023
    
    // 复杂模式匹配与正则表达式
    val logPattern = """(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)""".r
    
    def parseLogEntry(logLine: String): Option[(String, String, String)] = {
      logLine match {
        case logPattern(timestamp, level, message) => 
          Some((timestamp, level, message))
        case _ => 
          None
      }
    }
    
    val logLine1 = "2023-12-25 10:30:45 [INFO] Application started"
    val logLine2 = "2023-12-25 10:31:00 [ERROR] Connection failed"
    val logLine3 = "Invalid log line"
    
    println(parseLogEntry(logLine1))  // Some((2023-12-25 10:30:45,INFO,Application started))
    println(parseLogEntry(logLine2))  // Some((2023-12-25 10:31:00,ERROR,Connection failed))
    println(parseLogEntry(logLine3))  // None
    
    // 正则表达式高级操作
    val wordPattern = """\b\w+\b""".r
    
    // 统计单词数
    def countWords(text: String): Int = {
      wordPattern.findAllMatchIn(text).length
    }
    
    val text1 = "This is a sample text with several words"
    println(s"Word count: ${countWords(text1)}")  // Word count: 8
    
    // 查找并替换
    val censoredText = wordPattern.replaceAllIn(text1, "REDACTED")
    println(s"Censored text: $censoredText")  // Censored text: REDACTED REDACTED REDACTED REDACTED REDACTED REDACTED REDACTED REDACTED
    
    // 替换首字母大写
    val titleCaseText = wordPattern.replaceAllIn(text1, m => {
      val word = m.matched
      word.charAt(0).toUpper + word.substring(1).toLowerCase
    })
    println(s"Title case: $titleCaseText")  // Title case: This Is A Sample Text With Several Words
    
    // 解析CSV数据
    val csvPattern = """([^,]*),([^,]*),([^,]*)""".r
    
    def parseCsvLine(line: String): Option[(String, String, String)] = {
      line match {
        case csvPattern(col1, col2, col3) => Some((col1.trim, col2.trim, col3.trim))
        case _ => None
      }
    }
    
    val csvLine = "John Doe, 30, New York"
    println(parseCsvLine(csvLine))  // Some((John Doe,30,New York))
    
    val csvLine2 = "Jane Smith, 25"
    println(parseCsvLine(csvLine2))  // None (missing column)
    
    // 提取器示例
    object Even {
      def unapply(x: Int): Option[Int] = if (x % 2 == 0) Some(x) else None
    }
    
    def describeNumber(num: Int): String = num match {
      case Even(x) => s"$x is even"
      case x => s"$x is odd"
    }
    
    println(describeNumber(2))  // 2 is even
    println(describeNumber(3))  // 3 is odd
    
    // 自定义提取器
    object Email {
      def unapply(str: String): Option[(String, String)] = {
        val atIndex = str.indexOf('@')
        if (atIndex > 0 && str.indexOf('.', atIndex) > 0) {
          Some((str.substring(0, atIndex), str.substring(atIndex + 1)))
        } else None
      }
    }
    
    def validateEmail(email: String): String = email match {
      case Email(username, domain) if username.length >= 3 && domain.contains(".") => 
        s"Valid email: $username@$domain"
      case Email(_, _) => "Invalid email format"
      case _ => "Not an email"
    }
    
    println(validateEmail("user@example.com"))    // Valid email: user@example.com
    println(validateEmail("ab@domain.com"))      // Valid email: ab@domain.com
    println(validateEmail("a@domain.com"))       // Invalid email format
    println(validateEmail("user@domain"))        // Invalid email format
    println(validateEmail("not an email"))        // Not an email
  }
}