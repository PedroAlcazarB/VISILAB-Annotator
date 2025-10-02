<template>
  <div id="app">
    <!-- Pantalla de bienvenida -->
    <div v-if="currentView === 'welcome'" class="welcome-screen">
      <header class="welcome-header">
        <h1>VISILAB Annotator</h1>
        <nav>
          <a href="#" class="nav-link active">Inicio</a>
          <a href="#" class="nav-link" @click="goToDatasets">Anotador</a>
        </nav>
      </header>
      
      <div class="welcome-content">
        <h2>Bienvenido a VISILAB Annotator</h2>
        <p>Anota imágenes con bounding boxes y exporta en formato COCO.</p>
        <button @click="goToDatasets" class="btn btn-primary">
          Ir al anotador
        </button>
      </div>
    </div>

    <!-- Gestión de datasets -->
    <div v-else-if="currentView === 'datasets'" class="datasets-screen">
      <header class="app-header">
        <h1>VISILAB Annotator</h1>
        <nav>
          <a href="#" class="nav-link" @click="goToWelcome">Inicio</a>
          <a href="#" class="nav-link active">Anotador</a>
        </nav>
      </header>
      
      <DatasetManager @dataset-selected="selectDataset" />
    </div>

    <!-- Vista individual de dataset -->
    <div v-else-if="currentView === 'dataset'" class="dataset-screen">
      <DatasetView 
        :dataset="selectedDataset" 
        @go-back="goToDatasets"
      />
    </div>
  </div>
</template>

<script>
import DatasetManager from './components/DatasetManager.vue'
import DatasetView from './views/DatasetView.vue'

export default {
  name: 'App',
  components: {
    DatasetManager,
    DatasetView
  },
  data() {
    return {
      currentView: 'welcome', // 'welcome', 'datasets', 'dataset'
      selectedDataset: null
    }
  },
  methods: {
    goToWelcome() {
      this.currentView = 'welcome'
      this.selectedDataset = null
    },
    
    goToDatasets() {
      this.currentView = 'datasets'
      this.selectedDataset = null
    },
    
    selectDataset(dataset) {
      this.selectedDataset = dataset
      this.currentView = 'dataset'
    }
  }
}
</script>

<style>
/* Reset básico */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #2c3e50;
  min-height: 100vh;
}

/* Estilo del header */
.app-header, .welcome-header {
  background: #ffffff;
  border-bottom: 1px solid #e1e5e9;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1, .welcome-header h1 {
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
}

nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.nav-link.active {
  color: #0ea5e9;
  background: #e0f2fe;
}

/* Pantalla de bienvenida */
.welcome-screen {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 80px);
  text-align: center;
  color: white;
  padding: 2rem;
}

.welcome-content h2 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.welcome-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
}

/* Estilos para pantallas con header */
.datasets-screen, .dataset-screen {
  min-height: 100vh;
  background: #f8fafc;
}

/* Botones */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #0ea5e9;
  color: white;
}

.btn-primary:hover {
  background: #0284c7;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .app-header, .welcome-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .welcome-content h2 {
    font-size: 2rem;
  }
  
  nav {
    gap: 1rem;
  }
}
</style>
