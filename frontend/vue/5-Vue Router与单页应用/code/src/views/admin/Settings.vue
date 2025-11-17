<template>
  <div class="settings">
    <h2>系统设置</h2>
    
    <div class="settings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
        class="tab-button"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div class="tab-content">
      <!-- 基本设置 -->
      <div v-if="activeTab === 'general'" class="tab-pane">
        <form @submit.prevent="saveGeneralSettings">
          <div class="form-group">
            <label for="siteName">网站名称:</label>
            <input type="text" id="siteName" v-model="generalSettings.siteName" required>
          </div>
          <div class="form-group">
            <label for="siteDescription">网站描述:</label>
            <textarea 
              id="siteDescription" 
              v-model="generalSettings.siteDescription" 
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="adminEmail">管理员邮箱:</label>
            <input type="email" id="adminEmail" v-model="generalSettings.adminEmail" required>
          </div>
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                v-model="generalSettings.maintenanceMode"
              > 维护模式
            </label>
          </div>
          <button type="submit" class="btn btn-primary">保存设置</button>
        </form>
      </div>
      
      <!-- 邮件设置 -->
      <div v-if="activeTab === 'email'" class="tab-pane">
        <form @submit.prevent="saveEmailSettings">
          <div class="form-group">
            <label for="smtpHost">SMTP主机:</label>
            <input type="text" id="smtpHost" v-model="emailSettings.smtpHost" required>
          </div>
          <div class="form-group">
            <label for="smtpPort">SMTP端口:</label>
            <input type="number" id="smtpPort" v-model.number="emailSettings.smtpPort" required>
          </div>
          <div class="form-group">
            <label for="smtpUser">用户名:</label>
            <input type="text" id="smtpUser" v-model="emailSettings.smtpUser" required>
          </div>
          <div class="form-group">
            <label for="smtpPass">密码:</label>
            <input type="password" id="smtpPass" v-model="emailSettings.smtpPass" required>
          </div>
          <div class="form-group">
            <label for="fromEmail">发件人邮箱:</label>
            <input type="email" id="fromEmail" v-model="emailSettings.fromEmail" required>
          </div>
          <button type="submit" class="btn btn-primary">保存设置</button>
        </form>
      </div>
      
      <!-- 支付设置 -->
      <div v-if="activeTab === 'payment'" class="tab-pane">
        <form @submit.prevent="savePaymentSettings">
          <div class="form-group">
            <label>
              <input 
                type="radio" 
                v-model="paymentSettings.provider" 
                value="stripe"
              > Stripe
            </label>
          </div>
          <div class="form-group">
            <label>
              <input 
                type="radio" 
                v-model="paymentSettings.provider" 
                value="paypal"
              > PayPal
            </label>
          </div>
          
          <div v-if="paymentSettings.provider === 'stripe'">
            <div class="form-group">
              <label for="stripePublicKey">Stripe公钥:</label>
              <input type="text" id="stripePublicKey" v-model="paymentSettings.stripePublicKey" required>
            </div>
            <div class="form-group">
              <label for="stripeSecretKey">Stripe私钥:</label>
              <input type="password" id="stripeSecretKey" v-model="paymentSettings.stripeSecretKey" required>
            </div>
          </div>
          
          <div v-if="paymentSettings.provider === 'paypal'">
            <div class="form-group">
              <label for="paypalClientId">PayPal客户端ID:</label>
              <input type="text" id="paypalClientId" v-model="paymentSettings.paypalClientId" required>
            </div>
            <div class="form-group">
              <label for="paypalSecret">PayPal密钥:</label>
              <input type="password" id="paypalSecret" v-model="paymentSettings.paypalSecret" required>
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary">保存设置</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemSettings',
  data() {
    return {
      activeTab: 'general',
      tabs: [
        { id: 'general', name: '基本设置' },
        { id: 'email', name: '邮件设置' },
        { id: 'payment', name: '支付设置' }
      ],
      generalSettings: {
        siteName: '我的电商网站',
        siteDescription: '一个现代化的电商网站',
        adminEmail: 'admin@example.com',
        maintenanceMode: false
      },
      emailSettings: {
        smtpHost: 'smtp.example.com',
        smtpPort: 587,
        smtpUser: 'user@example.com',
        smtpPass: '',
        fromEmail: 'noreply@example.com'
      },
      paymentSettings: {
        provider: 'stripe',
        stripePublicKey: 'pk_test_XXXXXXXXXXXXXXXXXXXXXXXX',
        stripeSecretKey: 'sk_test_XXXXXXXXXXXXXXXXXXXXXXXX',
        paypalClientId: '',
        paypalSecret: ''
      }
    }
  },
  methods: {
    saveGeneralSettings() {
      alert('基本设置已保存!')
    },
    saveEmailSettings() {
      alert('邮件设置已保存!')
    },
    savePaymentSettings() {
      alert('支付设置已保存!')
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 1rem 0;
}

.settings-tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 2rem;
}

.tab-button {
  padding: 1rem 2rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #6c757d;
}

.tab-button.active {
  color: #42b983;
  border-bottom: 3px solid #42b983;
}

.tab-content {
  min-height: 300px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input[type="checkbox"],
.form-group input[type="radio"] {
  width: auto;
  margin-right: 0.5rem;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #359c6d;
}
</style>