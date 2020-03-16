import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const store = new Vuex.Store({
    state: {
        username: null,
    },
    getters: {},
    mutations: {
        setUsername(state, username) {
            state.username = username;
        }
    },
    actions: {
        register(context, username) {
            context.commit("setUsername", username);
        }
    }
});

export default store;