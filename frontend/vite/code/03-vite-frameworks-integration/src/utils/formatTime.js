/**
 * 格式化时间为相对时间或具体时间
 * @param {Date|string|number} date - 要格式化的时间
 * @param {Object} options - 格式化选项
 * @param {boolean} options.relative - 是否使用相对时间（如"5分钟前"）
 * @param {string} options.format - 当不使用相对时间时的格式类型：'full', 'short', 'time'
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(date, options = {}) {
  const {
    relative = true,
    format = 'full'
  } = options;

  const now = new Date();
  const targetDate = new Date(date);
  const diffInMs = now - targetDate;
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);

  // 如果启用相对时间且时间在合理范围内
  if (relative && diffInDays < 7) {
    if (diffInSeconds < 60) {
      return '刚刚';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}分钟前`;
    } else if (diffInHours < 24) {
      return `${diffInHours}小时前`;
    } else {
      return `${diffInDays}天前`;
    }
  }

  // 否则返回具体时间
  switch (format) {
    case 'short':
      return `${targetDate.getMonth() + 1}/${targetDate.getDate()}`;
    case 'time':
      return targetDate.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    case 'full':
    default:
      return targetDate.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
  }
}

/**
 * 格式化数字，添加千位分隔符
 * @param {number} num - 要格式化的数字
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}