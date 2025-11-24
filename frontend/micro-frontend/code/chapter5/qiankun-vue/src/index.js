import { createApp } from 'vue';
import App from './App';

let instance = null;

// 为了让主应用能够正确识别子应用，需要添加一些生命周期函数
export async function bootstrap() {
  console.log('Vue app bootstraped');
}

export async function mount(props) {
  console.log('Vue app mounted');
  instance = createApp(App);
  instance.mount('#root');
}

export async function unmount(props) {
  console.log('Vue app unmounted');
  instance.unmount();
  instance = null;
}