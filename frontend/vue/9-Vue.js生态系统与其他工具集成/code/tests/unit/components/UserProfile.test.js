import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import UserProfile from '../../../src/components/UserProfile.vue'

describe('UserProfile.vue', () => {
  it('renders user profile when passed', () => {
    const user = {
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://example.com/avatar.jpg'
    }
    
    const wrapper = mount(UserProfile, {
      props: { user }
    })
    
    expect(wrapper.text()).toContain(user.name)
    expect(wrapper.text()).toContain(user.email)
    expect(wrapper.find('img').exists()).toBe(true)
  })

  it('renders placeholder when no user is passed', () => {
    const wrapper = mount(UserProfile)
    
    expect(wrapper.text()).toContain('未登录')
    expect(wrapper.find('.placeholder').exists()).toBe(true)
  })

  it('emits login event when login button is clicked', async () => {
    const wrapper = mount(UserProfile)
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('login')
  })
})