<template>
  <div class="home-view">
    <!-- Mostrar login/registro si no está autenticado -->
    <LoginRegister v-if="!authStore.isAuthenticated" />
    
    <!-- Mostrar bienvenida si está autenticado -->
    <div v-else class="welcome-section">
      <h2>Bienvenido a VISILAB Annotator</h2>
      <p class="welcome-user">
        Hola, <strong>{{ authStore.user?.username || 'Usuario' }}</strong>!
      </p>
      <p>Anota imágenes con bounding boxes y exporta en formato COCO.</p>
      <div class="actions">
        <router-link to="/projects" class="btn primary">
          Ir al anotador
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import LoginRegister from '../components/LoginRegister.vue'

const authStore = useAuthStore()

// Inicializar autenticación al montar
onMounted(async () => {
  await authStore.init()
})
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

.welcome-section {
  max-width: 600px;
  margin: 3rem auto;
  padding: 2rem;
  text-align: center;
  background: #f9f9f9;
  border-radius: 8px;
}

.welcome-user {
  color: #667eea;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.actions {
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  color: white;
  background: #42b983;
  transition: background 0.2s;
  display: inline-block;
}

.btn:hover {
  background: #369e6f;
}
</style>