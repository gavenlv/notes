import { createApp } from 'vue';
import singleSpaVue from 'single-spa-vue';
import App from './App.vue';

const lifecycles = singleSpaVue({
  createApp,
  appOptions: {
    el: '#app-container',
  }
});

export const { bootstrap, mount, unmount } = lifecycles;