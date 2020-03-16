import Vue from 'vue'
import VueRouter from 'vue-router'
import V3 from '../components/V3'

Vue.use(VueRouter);

const router = new VueRouter({
    routes: [
        {path: '/demoV3', name: 'demoV3', component: V3},
        {path: '/', redirect: '/demoV3'}
    ]
});

export default router;
