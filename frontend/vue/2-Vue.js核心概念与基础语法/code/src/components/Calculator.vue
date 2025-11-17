<template>
  <div class="calculator">
    <h3>计算器示例</h3>
    <div class="display">
      <input v-model="displayValue" readonly>
    </div>
    <div class="buttons">
      <button @click="clear">C</button>
      <button @click="toggleSign">+/-</button>
      <button @click="appendOperator('/')">/</button>
      <button @click="appendOperator('*')">*</button>
      
      <button @click="appendNumber('7')">7</button>
      <button @click="appendNumber('8')">8</button>
      <button @click="appendNumber('9')">9</button>
      <button @click="appendOperator('-')">-</button>
      
      <button @click="appendNumber('4')">4</button>
      <button @click="appendNumber('5')">5</button>
      <button @click="appendNumber('6')">6</button>
      <button @click="appendOperator('+')">+</button>
      
      <button @click="appendNumber('1')">1</button>
      <button @click="appendNumber('2')">2</button>
      <button @click="appendNumber('3')">3</button>
      <button @click="calculate" rowspan="2" class="equals">=</button>
      
      <button @click="appendNumber('0')" colspan="2" class="zero">0</button>
      <button @click="appendDecimal">.</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalculatorComponent',
  data() {
    return {
      currentValue: 0,
      previousValue: 0,
      operator: null,
      waitingForOperand: false
    }
  },
  
  computed: {
    displayValue() {
      return this.currentValue.toString()
    }
  },
  
  methods: {
    clear() {
      this.currentValue = 0
      this.previousValue = 0
      this.operator = null
      this.waitingForOperand = false
    },
    
    toggleSign() {
      this.currentValue = -this.currentValue
    },
    
    appendDecimal() {
      if (this.waitingForOperand) {
        this.currentValue = 0
        this.waitingForOperand = false
      }
      
      if (this.displayValue.indexOf('.') === -1) {
        this.currentValue += '.'
      }
    },
    
    appendNumber(number) {
      if (this.waitingForOperand) {
        this.currentValue = number
        this.waitingForOperand = false
      } else {
        this.currentValue = this.displayValue === '0' ? number : this.displayValue + number
      }
    },
    
    appendOperator(nextOperator) {
      const parsedValue = parseFloat(this.displayValue)
      
      if (this.previousValue === 0) {
        this.previousValue = parsedValue
      } else if (this.operator) {
        const currentValue = this.previousValue || 0
        const newValue = this.calculate(currentValue, parsedValue, this.operator)
        
        this.currentValue = newValue
        this.previousValue = newValue
      }
      
      this.waitingForOperand = true
      this.operator = nextOperator
    },
    
    calculate() {
      const parsedValue = parseFloat(this.displayValue)
      
      if (this.previousValue !== 0 && this.operator) {
        const newValue = this.performCalculation(this.previousValue, parsedValue, this.operator)
        this.currentValue = newValue
        this.previousValue = 0
        this.operator = null
        this.waitingForOperand = true
      }
    },
    
    performCalculation(firstValue, secondValue, operator) {
      switch (operator) {
        case '+':
          return firstValue + secondValue
        case '-':
          return firstValue - secondValue
        case '*':
          return firstValue * secondValue
        case '/':
          return firstValue / secondValue
        default:
          return secondValue
      }
    }
  }
}
</script>

<style scoped>
.calculator {
  max-width: 300px;
  margin: 20px auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.display input {
  width: 100%;
  height: 50px;
  font-size: 24px;
  text-align: right;
  padding: 0 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  box-sizing: border-box;
}

.buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-gap: 10px;
}

button {
  height: 50px;
  font-size: 18px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
  cursor: pointer;
}

button:hover {
  background-color: #e9ecef;
}

.equals {
  grid-row: span 2;
}

.zero {
  grid-column: span 2;
}
</style>