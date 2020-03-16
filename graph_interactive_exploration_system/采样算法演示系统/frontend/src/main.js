import Vue from 'vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import router from './router/index'
import store from './store/index'

import App from './App.vue'

Vue.config.productionTip = false;
Vue.use(ElementUI);

new Vue({
    render: h => h(App),
    router: router,
    store: store,
}).$mount('#app');
