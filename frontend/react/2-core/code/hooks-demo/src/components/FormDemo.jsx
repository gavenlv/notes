import { useState } from 'react'
import { useTheme } from '../context/ThemeContext.jsx'
import useForm from '../hooks/useForm.js'

function FormDemo() {
  const { styles } = useTheme()
  const [submittedData, setSubmittedData] = useState(null)
  
  // 表单验证规则
  const validationRules = {
    name: {
      required: true,
      minLength: 2,
      maxLength: 50,
      message: '姓名长度必须在2-50个字符之间'
    },
    email: {
      required: true,
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      message: '请输入有效的邮箱地址'
    },
    age: {
      required: true,
      min: 18,
      max: 120,
      message: '年龄必须在18-120岁之间'
    },
    interests: {
      minLength: 1,
      message: '请至少选择一个兴趣爱好'
    },
    bio: {
      maxLength: 200,
      message: '个人简介不能超过200个字符'
    }
  }

  // 使用自定义的useForm Hook
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  } = useForm({
    name: '',
    email: '',
    age: '',
    interests: [],
    bio: '',
    subscribe: false
  }, validationRules)

  // 处理表单提交
  const onSubmit = (formData) => {
    console.log('表单提交数据:', formData)
    setSubmittedData(formData)
    // 这里可以添加API请求等后续操作
  }

  // 重置提交状态
  const resetSubmittedData = () => {
    setSubmittedData(null)
  }

  // 兴趣爱好选项
  const interestOptions = [
    { id: 'reading', label: '阅读' },
    { id: 'coding', label: '编程' },
    { id: 'gaming', label: '游戏' },
    { id: 'music', label: '音乐' },
    { id: 'sports', label: '运动' },
    { id: 'art', label: '艺术' }
  ]

  // 处理复选框选择
  const handleInterestChange = (interestId) => {
    const currentInterests = [...values.interests]
    const index = currentInterests.indexOf(interestId)
    
    if (index === -1) {
      currentInterests.push(interestId)
    } else {
      currentInterests.splice(index, 1)
    }
    
    handleChange({ target: { name: 'interests', value: currentInterests } })
  }

  // 表单字段组件
  const FormField = ({ label, name, type = 'text', placeholder = '', required = false, options = null, as = 'input' }) => {
    const isError = touched[name] && errors[name]
    
    return (
      <div className="form-field">
        <label htmlFor={name} className="form-label"
          style={{
            color: styles.color,
            fontWeight: 'bold',
            display: 'block',
            marginBottom: '0.5rem'
          }}
        >
          {label}
          {required && <span style={{ color: '#e53e3e' }}> *</span>}
        </label>
        
        {as === 'input' && type !== 'checkbox' && type !== 'radio' && (
          <input
            id={name}
            name={name}
            type={type}
            value={values[name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder={placeholder}
            className="form-input"
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '0.25rem',
              border: `1px solid ${isError ? '#e53e3e' : styles.borderColor}`,
              backgroundColor: styles.inputBackgroundColor || styles.backgroundColor,
              color: styles.color,
              fontSize: '1rem'
            }}
          />
        )}
        
        {as === 'textarea' && (
          <textarea
            id={name}
            name={name}
            value={values[name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder={placeholder}
            className="form-textarea"
            rows={4}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '0.25rem',
              border: `1px solid ${isError ? '#e53e3e' : styles.borderColor}`,
              backgroundColor: styles.inputBackgroundColor || styles.backgroundColor,
              color: styles.color,
              fontSize: '1rem',
              minHeight: '100px',
              resize: 'vertical'
            }}
          />
        )}
        
        {type === 'checkbox' && (
          <div className="checkbox-container">
            <input
              id={name}
              name={name}
              type="checkbox"
              checked={values[name] || false}
              onChange={handleChange}
              onBlur={handleBlur}
              style={{
                width: '1.25rem',
                height: '1.25rem',
                marginRight: '0.5rem',
                accentColor: styles.primaryColor
              }}
            />
            <span style={{ color: styles.color }}>{label}</span>
          </div>
        )}
        
        {options && (
          <div className="checkbox-group">
            {options.map(option => (
              <div key={option.id} className="checkbox-item">
                <input
                  id={`${name}-${option.id}`}
                  type="checkbox"
                  checked={values[name]?.includes(option.id) || false}
                  onChange={() => handleInterestChange(option.id)}
                  onBlur={() => handleBlur({ target: { name } })}
                  style={{
                    width: '1.25rem',
                    height: '1.25rem',
                    marginRight: '0.5rem',
                    accentColor: styles.primaryColor
                  }}
                />
                <label htmlFor={`${name}-${option.id}`}
                  style={{ color: styles.color, cursor: 'pointer' }}
                >
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )}
        
        {isError && (
          <p className="error-message"
            style={{
              color: '#e53e3e',
              fontSize: '0.875rem',
              marginTop: '0.25rem',
              marginBottom: 0
            }}
          >
            {errors[name]}
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="form-demo">
      <h2 style={{ color: styles.primaryColor }}>useForm Hook 表单演示</h2>
      <p className="demo-description">
        这个演示展示了如何使用自定义的useForm Hook来管理表单状态、验证和提交。
      </p>

      <form 
        onSubmit={handleSubmit(onSubmit)}
        className="demo-form"
        style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}
      >
        <div className="form-header">
          <h3 style={{ color: styles.secondaryColor }}>用户注册表单</h3>
          <p style={{ color: styles.color }}>请填写以下信息完成注册（带 * 的字段为必填项）</p>
        </div>

        <div className="form-content">
          <FormField
            label="姓名"
            name="name"
            placeholder="请输入您的姓名"
            required
          />
          
          <FormField
            label="邮箱"
            name="email"
            type="email"
            placeholder="请输入您的邮箱地址"
            required
          />
          
          <FormField
            label="年龄"
            name="age"
            type="number"
            placeholder="请输入您的年龄"
            required
          />
          
          <FormField
            label="兴趣爱好"
            name="interests"
            options={interestOptions}
            required
          />
          
          <FormField
            label="个人简介"
            name="bio"
            as="textarea"
            placeholder="请简要介绍一下自己"
          />
          
          <FormField
            label="订阅新闻通讯"
            name="subscribe"
            type="checkbox"
          />
        </div>

        <div className="form-actions"
          style={{ borderTop: `1px solid ${styles.borderColor}` }}
        >
          <button 
            type="submit" 
            disabled={!isValid}
            className="submit-btn"
            style={{
              backgroundColor: isValid ? styles.primaryColor : '#a0aec0',
              color: '#fff',
              borderColor: isValid ? styles.primaryColor : '#a0aec0',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.25rem',
              fontSize: '1rem',
              fontWeight: 'bold',
              cursor: isValid ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s'
            }}
          >
            提交表单
          </button>
        </div>
      </form>

      {submittedData && (
        <div className="submission-result" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.primaryColor }}>
          <h3 style={{ color: styles.primaryColor }}>表单提交成功！</h3>
          <div className="submitted-data">
            <div className="data-item">
              <span className="data-label">姓名:</span>
              <span className="data-value">{submittedData.name}</span>
            </div>
            <div className="data-item">
              <span className="data-label">邮箱:</span>
              <span className="data-value">{submittedData.email}</span>
            </div>
            <div className="data-item">
              <span className="data-label">年龄:</span>
              <span className="data-value">{submittedData.age}</span>
            </div>
            <div className="data-item">
              <span className="data-label">兴趣爱好:</span>
              <span className="data-value">
                {submittedData.interests.map(interestId => {
                  const option = interestOptions.find(opt => opt.id === interestId)
                  return option ? option.label : interestId
                }).join(', ')}
              </span>
            </div>
            <div className="data-item">
              <span className="data-label">个人简介:</span>
              <span className="data-value">{submittedData.bio || '未填写'}</span>
            </div>
            <div className="data-item">
              <span className="data-label">订阅新闻通讯:</span>
              <span className="data-value">{submittedData.subscribe ? '是' : '否'}</span>
            </div>
          </div>
          <button 
            onClick={resetSubmittedData}
            className="reset-btn"
            style={{
              backgroundColor: 'transparent',
              color: styles.secondaryColor,
              borderColor: styles.secondaryColor,
              padding: '0.5rem 1rem',
              borderRadius: '0.25rem',
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}
          >
            清除结果
          </button>
        </div>
      )}

      <div className="code-explanation" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>自定义Hook useForm 代码示例</h3>
        <pre><code>
{`// 自定义Hook - 用于表单管理
function useForm(initialValues, validationRules = {}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validateField = (name, value) => {
    if (!validationRules[name]) return '';
    
    const rules = validationRules[name];
    
    if (rules.required && (!value || (Array.isArray(value) && value.length === 0))) {
      return rules.message || '此字段为必填项';
    }
    
    if (value) {
      if (rules.minLength && value.length < rules.minLength) {
        return rules.message || '至少需要' + rules.minLength + '个字符';
      }
      
      if (rules.maxLength && value.length > rules.maxLength) {
        return rules.message || '最多只能输入' + rules.maxLength + '个字符';
      }
      
      if (rules.min && Number(value) < rules.min) {
        return rules.message || '不能小于' + rules.min + '';
      }
      
      if (rules.max && Number(value) > rules.max) {
        return rules.message || '不能大于' + rules.max + '';
      }
      
      if (rules.pattern && !rules.pattern.test(value)) {
        return rules.message || '格式不正确';
      }
    }
    
    return '';
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setValues(prev => ({
      ...prev,
      [name]: fieldValue
    }));
    
    const error = validateField(name, fieldValue);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
  };

  const handleBlur = (event) => {
    const { name } = event.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
  };

  const handleSubmit = (onSubmit) => (event) => {
    event.preventDefault();
    
    const newTouched = {};
    const newErrors = {};
    
    Object.keys(values).forEach(key => {
      newTouched[key] = true;
      newErrors[key] = validateField(key, values[key]);
    });
    
    setTouched(newTouched);
    setErrors(newErrors);
    
    const hasErrors = Object.values(newErrors).some(error => error !== '');
    
    if (!hasErrors && onSubmit) {
      onSubmit(values);
    }
  };

  const isValid = Object.keys(values).every(key => {
    return touched[key] ? errors[key] === '' : true;
  });

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  };
}

export default useForm;`}
        </code></pre>
      </div>
    </div>
  )
}

export default FormDemo
