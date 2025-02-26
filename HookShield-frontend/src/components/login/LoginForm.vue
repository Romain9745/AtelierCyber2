

<template>
    <div>
        <section>
        <div class="flex flex-col items-center ">
                <img class="w-50 h-50 mr-2" src="/HookShield_logo.svg" alt="logo">
            <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
                <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
                    <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
                        Sign in to your account
                    </h1>
                    <form class="space-y-4 md:space-y-6" action="#">
                        <div>
                            <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Your email</label>
                            <input type="email" v-model="email" name="email" id="email" class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="name@company.com" required="">
                        </div>
                        <div>
                            <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Password</label>
                            <input type="password" v-model="password" name="password" id="password" placeholder="••••••••" class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" required="">
                        </div>
                        <div class="flex items-center justify-between">
                            <div class="flex items-start">
                                <div class="flex items-center h-5">
                                    <input id="remember" aria-describedby="remember" type="checkbox" class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 dark:ring-offset-gray-800" required="">
                                </div>
                                <div class="ml-3 text-sm">
                                    <label for="remember" class="text-gray-500 dark:text-gray-300">Remember me</label>
                                </div>
                            </div>
                            <a href="#" class="text-sm font-medium text-primary-600 hover:underline dark:text-primary-500">Forgot password?</a>
                        </div>
                        <p v-if="Loginerror" class="text-red-500 text-sm text-center">{{ Loginerror }}</p>
                        <button class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors" @click.prevent="handleSignIn">
                            Sign In
                        </button>
                    </form>
                </div>
            </div>
        </div>
        </section> 
    </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import { useAuthStore } from "@/store/auth.js";

export default {
    name: 'LoginForm',
    setup() {
        

        const router = useRouter();
        const authStore = useAuthStore();
        const email = ref('');
        const password = ref('');
        const Loginerror = ref('');


        onMounted(async () => {
            if (authStore.isAuthenticated) {
            router.push('/'); // Redirect to home if already authenticated
            }
        });

        const handleSignIn = async () => {
            try {
                Loginerror.value = '';
                await authStore.login(email.value,password.value).then(() => {
                    if (authStore.isAuthenticated) router.push({ name: "home" });
                });
            } catch (e) {
                Loginerror.value = "Invalid credentials";
                console.error(e);
            }
        }

        return {
            email,
            password,
            Loginerror,
            handleSignIn
        }
    }
}
</script>

<style scoped>
.space-y-4 > * + *, 
.space-y-6 > * + *, 
.md\:space-y-6 > * + * {
    margin-top: 10px !important;
}

.bg-img {
  background-color: #f4f4f4;
  border-radius: 10px;
}
</style>
