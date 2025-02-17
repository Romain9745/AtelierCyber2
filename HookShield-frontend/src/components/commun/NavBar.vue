<template>
  <header class="h-[10vh] bg-blue-600 text-white p-4 flex justify-between items-center">
      <img class="h-full mr-2" src="/HookShield_logo.svg" alt="logo">
    <div class="flex items-center gap-3">
      <div class="h-full flex flex-col items-center">
        <img
          src="https://images.pexels.com/photos/2071882/pexels-photo-2071882.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
          class="rounded-full w-10 h-10 mb-2"
          alt="Avatar"
        />
        <span>Nom d'utilisateur</span>
      </div>
      <button class="h-full px-4 py-2 bg-red-500 rounded hover:bg-red-600">Déconnexion</button>
    </div>
  </header>
</template>