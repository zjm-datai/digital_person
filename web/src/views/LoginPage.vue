<template>
  <div class="login-wrap">
    <div class="card">
      <h2>登录</h2>

      <form @submit.prevent="onSubmit">
        <div class="field">
          <label>Email</label>
          <input v-model.trim="email" type="email" autocomplete="username" required />
        </div>

        <div class="field">
          <label>Password</label>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </div>

        <label class="remember">
          <input v-model="rememberMe" type="checkbox" />
          记住我
        </label>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="btn" :disabled="auth.loading">
          {{ auth.loading ? "登录中..." : "登录" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const error = ref<string | null>(null);

async function onSubmit() {
  error.value = null;
  try {
    await auth.login(email.value, password.value, rememberMe.value);

    const redirect = (route.query.redirect as string) || "/home";
    await router.replace(redirect);
  } catch (e: any) {
    error.value = e?.message || "登录失败";
  }
}
</script>

<style scoped>

.login-wrap { 
    min-height: 100vh; 
    display: grid; 
    place-items: center; 
    padding: 24px; 
}
.card { 
    width: min(420px, 100%); 
    border: 1px solid #e7e7e7; 
    border-radius: 12px; 
    padding: 18px; 
}
.field { 
    margin: 12px 0; 
    display: grid; 
    gap: 6px; 
}

input { 
    height: 38px; 
    padding: 0 10px; 
    border: 1px solid #d8d8d8; 
    border-radius: 8px; 
}
.remember { display:flex; align-items:center; gap: 8px; font-size: 14px; margin: 12px 0; }
.error { color: #d33; margin: 10px 0; }
.btn { width: 100%; height: 40px; border: 0; border-radius: 10px; cursor: pointer; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

</style>
