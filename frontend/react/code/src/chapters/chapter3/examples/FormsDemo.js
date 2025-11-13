import React, { useState } from 'react';

// 基本输入框
function BasicInputExample() {
  const [value, setValue] = useState('');
  
  return (
    <div className="example-section">
      <h3>基本输入框</h3>
      
      <div className="example-group">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="输入文本"
        />
        <p>输入的值: {value}</p>
        <p>字符数: {value.length}</p>
      </div>
    </div>
  );
}

// 多行文本框
function TextAreaExample() {
  const [value, setValue] = useState('');
  
  return (
    <div className="example-section">
      <h3>多行文本框</h3>
      
      <div className="example-group">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="输入多行文本"
          rows={4}
          style={{ width: '100%' }}
        />
        <p>行数: {value.split('\n').length}</p>
        <p>字符数: {value.length}</p>
      </div>
    </div>
  );
}

// 选择框
function SelectExample() {
  const [value, setValue] = useState('option1');
  
  return (
    <div className="example-section">
      <h3>选择框</h3>
      
      <div className="example-group">
        <select value={value} onChange={(e) => setValue(e.target.value)}>
          <option value="option1">选项1</option>
          <option value="option2">选项2</option>
          <option value="option3">选项3</option>
        </select>
        <p>选择的值: {value}</p>
      </div>
    </div>
  );
}

// 复选框
function CheckboxExample() {
  const [isChecked, setIsChecked] = useState(false);
  
  return (
    <div className="example-section">
      <h3>复选框</h3>
      
      <div className="example-group">
        <label>
          <input
            type="checkbox"
            checked={isChecked}
            onChange={(e) => setIsChecked(e.target.checked)}
          />
          同意条款
        </label>
        <p>是否同意: {isChecked ? '是' : '否'}</p>
      </div>
    </div>
  );
}

// 单选按钮
function RadioExample() {
  const [value, setValue] = useState('option1');
  
  return (
    <div className="example-section">
      <h3>单选按钮</h3>
      
      <div className="example-group">
        <label>
          <input
            type="radio"
            value="option1"
            checked={value === 'option1'}
            onChange={(e) => setValue(e.target.value)}
          />
          选项1
        </label>
        <label>
          <input
            type="radio"
            value="option2"
            checked={value === 'option2'}
            onChange={(e) => setValue(e.target.value)}
          />
          选项2
        </label>
        <label>
          <input
            type="radio"
            value="option3"
            checked={value === 'option3'}
            onChange={(e) => setValue(e.target.value)}
          />
          选项3
        </label>
        <p>选择的值: {value}</p>
      </div>
    </div>
  );
}

// 文件上传
function FileInputExample() {
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState(0);
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      setFileSize(file.size);
    } else {
      setFileName('');
      setFileSize(0);
    }
  };
  
  return (
    <div className="example-section">
      <h3>文件上传</h3>
      
      <div className="example-group">
        <input
          type="file"
          onChange={handleFileChange}
        />
        {fileName && (
          <div>
            <p>文件名: {fileName}</p>
            <p>文件大小: {fileSize} 字节</p>
          </div>
        )}
      </div>
    </div>
  );
}

// 表单验证
function FormValidationExample() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 清除当前字段的错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = '邮箱不能为空';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.password) {
      newErrors.password = '密码不能为空';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码长度至少6位';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次密码不一致';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      alert('表单验证通过！');
    }
  };
  
  return (
    <div className="example-section">
      <h3>表单验证</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>邮箱:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <div className="error-message">{errors.email}</div>}
        </div>
        
        <div className="form-group">
          <label>密码:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className={errors.password ? 'error' : ''}
          />
          {errors.password && <div className="error-message">{errors.password}</div>}
        </div>
        
        <div className="form-group">
          <label>确认密码:</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            className={errors.confirmPassword ? 'error' : ''}
          />
          {errors.confirmPassword && <div className="error-message">{errors.confirmPassword}</div>}
        </div>
        
        <button type="submit">提交</button>
      </form>
    </div>
  );
}

// 综合表单示例
function ComprehensiveFormExample() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    age: '',
    gender: 'male',
    hobbies: [],
    country: 'china',
    bio: '',
    newsletter: false
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox' && name === 'hobbies') {
      // 处理复选框组
      const { value: hobbyValue } = e.target;
      setFormData(prev => {
        const hobbies = checked
          ? [...prev.hobbies, hobbyValue]
          : prev.hobbies.filter(h => h !== hobbyValue);
        return { ...prev, hobbies };
      });
    } else if (type === 'checkbox') {
      // 处理单个复选框
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      // 处理其他输入类型
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // 清除错误
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = '用户名不能为空';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.age) {
      newErrors.age = '年龄不能为空';
    } else if (isNaN(formData.age) || formData.age < 18 || formData.age > 100) {
      newErrors.age = '年龄必须在18-100之间';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      setIsSubmitted(true);
      console.log('表单数据:', formData);
    }
  };
  
  const handleReset = () => {
    setFormData({
      username: '',
      email: '',
      age: '',
      gender: 'male',
      hobbies: [],
      country: 'china',
      bio: '',
      newsletter: false
    });
    setErrors({});
    setIsSubmitted(false);
  };
  
  if (isSubmitted) {
    return (
      <div className="example-section">
        <h3>表单提交成功</h3>
        <div className="success-message">
          <h4>提交的数据:</h4>
          <pre>{JSON.stringify(formData, null, 2)}</pre>
          <button onClick={handleReset}>重新填写</button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="example-section">
      <h3>综合表单示例</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>用户名:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className={errors.username ? 'error' : ''}
          />
          {errors.username && <div className="error-message">{errors.username}</div>}
        </div>
        
        <div className="form-group">
          <label>邮箱:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <div className="error-message">{errors.email}</div>}
        </div>
        
        <div className="form-group">
          <label>年龄:</label>
          <input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
            className={errors.age ? 'error' : ''}
          />
          {errors.age && <div className="error-message">{errors.age}</div>}
        </div>
        
        <div className="form-group">
          <label>性别:</label>
          <div>
            <label>
              <input
                type="radio"
                name="gender"
                value="male"
                checked={formData.gender === 'male'}
                onChange={handleChange}
              />
              男
            </label>
            <label>
              <input
                type="radio"
                name="gender"
                value="female"
                checked={formData.gender === 'female'}
                onChange={handleChange}
              />
              女
            </label>
          </div>
        </div>
        
        <div className="form-group">
          <label>爱好:</label>
          <div>
            <label>
              <input
                type="checkbox"
                name="hobbies"
                value="reading"
                checked={formData.hobbies.includes('reading')}
                onChange={handleChange}
              />
              阅读
            </label>
            <label>
              <input
                type="checkbox"
                name="hobbies"
                value="sports"
                checked={formData.hobbies.includes('sports')}
                onChange={handleChange}
              />
              运动
            </label>
            <label>
              <input
                type="checkbox"
                name="hobbies"
                value="music"
                checked={formData.hobbies.includes('music')}
                onChange={handleChange}
              />
              音乐
            </label>
          </div>
        </div>
        
        <div className="form-group">
          <label>国家:</label>
          <select
            name="country"
            value={formData.country}
            onChange={handleChange}
          >
            <option value="china">中国</option>
            <option value="usa">美国</option>
            <option value="japan">日本</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>自我介绍:</label>
          <textarea
            name="bio"
            value={formData.bio}
            onChange={handleChange}
            rows={4}
          />
        </div>
        
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              name="newsletter"
              checked={formData.newsletter}
              onChange={handleChange}
            />
            订阅新闻通讯
          </label>
        </div>
        
        <div className="form-actions">
          <button type="submit">提交</button>
          <button type="button" onClick={handleReset}>重置</button>
        </div>
      </form>
    </div>
  );
}

// 实时表单预览
function LivePreviewForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    color: '#007bff',
    fontSize: '16px',
    borderRadius: '4px',
    borderStyle: 'solid'
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const previewStyle = {
    backgroundColor: formData.color,
    fontSize: formData.fontSize,
    borderRadius: formData.borderRadius,
    borderStyle: formData.borderStyle,
    padding: '20px',
    color: 'white',
    maxWidth: '300px'
  };
  
  return (
    <div className="example-section">
      <h3>实时表单预览</h3>
      
      <div className="preview-container">
        <div className="form-controls">
          <div className="form-group">
            <label>标题:</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="输入标题"
            />
          </div>
          
          <div className="form-group">
            <label>描述:</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="输入描述"
              rows={3}
            />
          </div>
          
          <div className="form-group">
            <label>背景颜色:</label>
            <input
              type="color"
              name="color"
              value={formData.color}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label>字体大小:</label>
            <select
              name="fontSize"
              value={formData.fontSize}
              onChange={handleChange}
            >
              <option value="14px">小</option>
              <option value="16px">中</option>
              <option value="18px">大</option>
              <option value="24px">特大</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>圆角大小:</label>
            <select
              name="borderRadius"
              value={formData.borderRadius}
              onChange={handleChange}
            >
              <option value="0">无圆角</option>
              <option value="4px">小圆角</option>
              <option value="8px">中圆角</option>
              <option value="16px">大圆角</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>边框样式:</label>
            <select
              name="borderStyle"
              value={formData.borderStyle}
              onChange={handleChange}
            >
              <option value="none">无边框</option>
              <option value="solid">实线</option>
              <option value="dashed">虚线</option>
              <option value="dotted">点线</option>
            </select>
          </div>
        </div>
        
        <div className="preview-box">
          <h4>预览:</h4>
          <div style={previewStyle}>
            <h3>{formData.title || '标题'}</h3>
            <p>{formData.description || '描述内容'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export const FormsDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>表单处理示例</h2>
        <p>本示例演示了React中各种表单元素的处理方式，包括输入框、文本区域、选择框、复选框、单选按钮、文件上传等，以及表单验证和实时预览功能。</p>
      </div>

      <div className="examples-grid">
        <BasicInputExample />
        <TextAreaExample />
        <SelectExample />
        <CheckboxExample />
        <RadioExample />
        <FileInputExample />
        <FormValidationExample />
        <ComprehensiveFormExample />
        <LivePreviewForm />
      </div>
      
      <div className="demo-info">
        <h3>表单处理要点</h3>
        <ul>
          <li>使用受控组件模式，让React控制表单数据流</li>
          <li>为表单元素添加value和onChange属性</li>
          <li>不同类型的表单元素有各自的value处理方式</li>
          <li>表单验证应该在提交前进行，提供即时反馈</li>
          <li>处理复选框组时需要使用数组存储选中的值</li>
          <li>实时预览可以增强用户体验，特别是对于可视化配置</li>
        </ul>
      </div>
    </div>
  );
};