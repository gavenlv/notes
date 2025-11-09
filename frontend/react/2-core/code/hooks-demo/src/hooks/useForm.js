import { useState, useCallback } from 'react'

/**
 * 自定义Hook - 用于表单状态管理和验证
 * 
 * @param {Object} initialValues - 表单初始值
 * @param {Object} validateRules - 表单验证规则
 * @returns {Object} 包含表单状态和操作方法的对象
 */
function useForm(initialValues = {}, validateRules = {}) {
  // 表单值状态
  const [values, setValues] = useState(initialValues)
  // 表单错误状态
  const [errors, setErrors] = useState({})
  // 表单触摸状态（用于跟踪哪些字段被访问过）
  const [touched, setTouched] = useState({})
  // 表单提交状态
  const [isSubmitting, setIsSubmitting] = useState(false)

  /**
   * 验证单个字段
   * @param {string} name - 字段名
   * @param {any} value - 字段值
   * @returns {string|null} 错误信息或null
   */
  const validateField = (name, value) => {
    // 获取该字段的验证规则
    const rules = validateRules[name]
    if (!rules) return null

    // 必填验证
    if (rules.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return rules.requiredMessage || `${name} is required`
    }

    // 最小长度验证
    if (rules.minLength && value && value.length < rules.minLength) {
      return rules.minLengthMessage || `${name} must be at least ${rules.minLength} characters`
    }

    // 最大长度验证
    if (rules.maxLength && value && value.length > rules.maxLength) {
      return rules.maxLengthMessage || `${name} must be at most ${rules.maxLength} characters`
    }

    // 正则表达式验证
    if (rules.pattern && value && !rules.pattern.test(value)) {
      return rules.patternMessage || `${name} is invalid`
    }

    // 自定义验证函数
    if (rules.validate && typeof rules.validate === 'function') {
      const validationResult = rules.validate(value, values)
      if (validationResult !== true) {
        return validationResult || `${name} is invalid`
      }
    }

    return null
  }

  /**
   * 验证整个表单
   * @returns {Object} 错误对象
   */
  const validateForm = useCallback(() => {
    const newErrors = {}

    // 验证每个字段
    Object.keys(validateRules).forEach(name => {
      const error = validateField(name, values[name])
      if (error) {
        newErrors[name] = error
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [values, validateRules])

  /**
   * 处理输入变化
   * @param {Event} e - 输入事件
   */
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target
    // 处理复选框和单选按钮的特殊情况
    const fieldValue = type === 'checkbox' || type === 'radio' ? checked : value

    // 更新表单值
    setValues(prev => ({
      ...prev,
      [name]: fieldValue
    }))

    // 如果字段已经被触摸，则实时验证
    if (touched[name]) {
      const error = validateField(name, fieldValue)
      setErrors(prev => ({
        ...prev,
        [name]: error
      }))
    }
  }, [touched])

  /**
   * 处理字段失去焦点
   * @param {Event} e - 失焦事件
   */
  const handleBlur = useCallback((e) => {
    const { name } = e.target
    
    // 设置字段为已触摸
    setTouched(prev => ({
      ...prev,
      [name]: true
    }))

    // 验证该字段
    const error = validateField(name, values[name])
    setErrors(prev => ({
      ...prev,
      [name]: error
    }))
  }, [values])

  /**
   * 手动设置字段值
   * @param {string} name - 字段名
   * @param {any} value - 字段值
   */
  const setFieldValue = useCallback((name, value) => {
    setValues(prev => ({
      ...prev,
      [name]: value
    }))

    if (touched[name]) {
      const error = validateField(name, value)
      setErrors(prev => ({
        ...prev,
        [name]: error
      }))
    }
  }, [touched])

  /**
   * 重置表单
   */
  const reset = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
    setIsSubmitting(false)
  }, [initialValues])

  /**
   * 处理表单提交
   * @param {Function} onSubmit - 提交成功后的回调函数
   */
  const handleSubmit = useCallback((onSubmit) => async (e) => {
    e.preventDefault()
    
    // 标记所有字段为已触摸
    const allTouched = Object.keys(initialValues).reduce((acc, key) => {
      acc[key] = true
      return acc
    }, {})
    setTouched(allTouched)

    // 验证表单
    const isValid = validateForm()
    if (!isValid) return

    // 设置提交状态
    setIsSubmitting(true)
    
    try {
      // 执行提交回调
      await onSubmit(values)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }, [values, validateForm, initialValues])

  // 返回表单相关状态和方法
  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    reset,
    validateForm
  }
}

export default useForm
