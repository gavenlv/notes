import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import UserProfile from '@/components/UserProfile.vue';
import apiClient from '@/utils/apiClient';
import { useDebug } from '@/composables/useDebug';

// Mock composables
vi.mock('@/composables/useDebug', () => ({
  useDebug: () => ({
    logDebug: vi.fn(),
    isDebugEnabled: { value: false }
  })
}));

// Mock API client
vi.mock('@/utils/apiClient', () => ({
  default: {
    get: vi.fn(),
    put: vi.fn()
  }
}));

describe('UserProfile.vue', () => {
  beforeEach(() => {
    // 清除所有模拟调用历史
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    const wrapper = mount(UserProfile);
    expect(wrapper.find('div').text()).toBe('Loading...');
  });

  it('fetches and displays user data', async () => {
    // 模拟API响应
    const mockUser = { id: 1, name: 'John Doe', email: 'john@example.com' };
    (apiClient.get as jest.Mock).mockResolvedValue({ data: mockUser });

    const wrapper = mount(UserProfile);
    await wrapper.vm.$nextTick(); // 等待异步操作完成

    // 验证API被调用
    expect(apiClient.get).toHaveBeenCalledWith('/user/profile');

    // 验证用户数据显示
    expect(wrapper.text()).toContain('John Doe');
    expect(wrapper.text()).toContain('john@example.com');
  });

  it('handles fetch error gracefully', async () => {
    // 模拟API错误
    (apiClient.get as jest.Mock).mockRejectedValue(new Error('Network error'));

    const wrapper = mount(UserProfile);
    await wrapper.vm.$nextTick(); // 等待异步操作完成

    // 验证错误处理
    expect(wrapper.text()).toContain('No user data');
  });

  it('updates user data correctly', async () => {
    const mockUser = { id: 1, name: 'John Doe', email: 'john@example.com' };
    const updatedUser = { ...mockUser, name: 'John Doe (updated)' };
    
    // 模拟API响应
    (apiClient.get as jest.Mock).mockResolvedValue({ data: mockUser });
    (apiClient.put as jest.Mock).mockResolvedValue({ data: updatedUser });

    const wrapper = mount(UserProfile);
    await wrapper.vm.$nextTick(); // 等待初始数据加载

    // 触发更新操作
    await wrapper.find('button').trigger('click');
    
    // 验证PUT请求被调用
    expect(apiClient.put).toHaveBeenCalledWith('/user/profile', updatedUser);
  });
});